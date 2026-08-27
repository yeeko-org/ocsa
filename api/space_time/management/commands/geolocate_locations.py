"""Revisión y backfill de la geolocalización derivada de las ubicaciones.

`--review` recorre las ubicaciones con proyecto y saca un CSV con lo
capturado contra lo calculado, sin escribir; `--fill` aplica «solo
vacíos» sobre todo el universo con geometría; `--revert` deshace un
`--fill` a partir del respaldo que este dejó.

Nunca llama a `Location.save()`: ese método propaga el estatus del
proyecto y el backfill no debe mover el estatus de nadie. Escribe con
`bulk_update`.
"""

import csv
import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from space_time.geolocate import apply_geolocation, resolve_geometry, \
    resolve_point
from space_time.geometry import has_geometry_q
from space_time.models import Location

DEFAULT_OUT = ".claude/geolocate_review.csv"
DEFAULT_BACKUP = ".claude/geolocate_fill_{day}.json"
COMPARED_FIELDS = ("state", "municipality", "locality")
UPDATED_FIELDS = [
    "state", "municipality", "locality",
    "latitude", "longitude", "nearby_localities"]
# Lo que el respaldo guarda por ubicación. Son los `_id` y no los
# objetos porque el respaldo es JSON y `--revert` escribe con
# `bulk_update`. `status_location` no está, y no debe estar: ni el
# backfill ni su reversa mueven el estatus de nadie.
BACKUP_FIELDS = (
    "state_id", "municipality_id", "locality_id",
    "latitude", "longitude", "nearby_localities")
BATCH_SIZE = 500


class Command(BaseCommand):
    help = "Revisa o rellena la geolocalización derivada de las ubicaciones"

    def add_arguments(self, parser):
        parser.add_argument(
            "--review", action="store_true",
            help="Compara lo capturado con lo calculado y escribe el CSV")
        parser.add_argument(
            "--fill", action="store_true",
            help="Llena lo vacío y recalcula los campos derivados")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Con --fill, cuenta lo que llenaría sin escribir")
        parser.add_argument(
            "--out", default=DEFAULT_OUT,
            help=f"Ruta del CSV de revisión (default: {DEFAULT_OUT})")
        parser.add_argument(
            "--limit", type=int,
            help="Acota el universo, para probar el comando")
        parser.add_argument(
            "--backup", default="",
            help="Ruta del respaldo que escribe --fill (default: "
                 + DEFAULT_BACKUP.format(day="<fecha>") + ")")
        parser.add_argument(
            "--revert", default="",
            help="Restaura los valores previos de un respaldo de --fill")

    def handle(self, *args, **options):
        if options["revert"]:
            for line in Reverter(options["revert"]).run():
                self.stdout.write(line)
            return
        if not options["review"] and not options["fill"]:
            self.stdout.write(
                "Nada que hacer: elige --review, --fill o --revert.")
            return
        if options["review"]:
            for line in Reviewer(options["out"], options["limit"]).run():
                self.stdout.write(line)
        if options["fill"]:
            backup = options["backup"] or DEFAULT_BACKUP.format(
                day=date.today().isoformat())
            filler = Filler(options["dry_run"], options["limit"], backup)
            for line in filler.run():
                self.stdout.write(line)


def located(limit: int | None = None, with_project: bool = False,
            with_relations: bool = False):
    """Ubicaciones con geometría, que son las únicas geolocalizables."""
    queryset = Location.objects.filter(has_geometry_q()).select_related(
        "state", "municipality", "locality", "project")
    if with_project:
        queryset = queryset.filter(project__isnull=False)
    if with_relations:
        queryset = queryset.prefetch_related("municipalities")
    queryset = queryset.order_by("id")
    return queryset[:limit] if limit else queryset


def resolve(location):
    """Resolución que corresponde al tipo de la ubicación."""
    if location.type_location == "point":
        return resolve_point(
            location.latitude, location.longitude, location.state_id)
    return resolve_geometry(location.geojson, location.state_id)


def computed_value(resolution, name: str):
    """Valor calculado de un campo comparable, sea punto o trazo."""
    if name != "municipality":
        return getattr(resolution, name, None)
    return getattr(
        resolution, "municipality",
        getattr(resolution, "single_municipality", None))


class Reviewer:
    """Compara capturado contra calculado; no escribe en la base."""

    def __init__(self, out: str, limit: int | None):
        self.out = Path(out)
        self.limit = limit
        self.reviewed = 0
        self.mismatches = {name: 0 for name in COMPARED_FIELDS}
        self.empty = {name: 0 for name in COMPARED_FIELDS}
        self.rows: list[dict] = []

    def run(self) -> list[str]:
        for location in located(self.limit, with_project=True).iterator(
                chunk_size=BATCH_SIZE):
            self.review(location)
        self.write_csv()
        return self.report()

    def review(self, location) -> None:
        self.reviewed += 1
        resolution = resolve(location)
        row = {
            "id": location.pk,
            "proyecto_id": location.project_id,
            "proyecto": str(location.project or ""),
            "tipo": location.type_location,
        }
        differs = False
        for name in COMPARED_FIELDS:
            captured = getattr(location, name)
            computed = computed_value(resolution, name)
            row[f"{name}_capturado"] = str(captured or "")
            row[f"{name}_calculado"] = str(computed or "")
            if captured is None:
                self.empty[name] += 1
                if computed is not None:
                    differs = True
            elif computed is not None and computed.pk != captured.pk:
                self.mismatches[name] += 1
                differs = True
        row["municipios_atravesados"] = "; ".join(
            municipality.name
            for municipality, _ in getattr(resolution, "municipalities", []))
        if differs:
            self.rows.append(row)

    def write_csv(self) -> None:
        if not self.rows:
            return
        self.out.parent.mkdir(parents=True, exist_ok=True)
        with self.out.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)

    def report(self) -> list[str]:
        lines = [
            f"Revisadas (con proyecto y con geometría): {self.reviewed}",
            f"Filas con alguna diferencia: {len(self.rows)}",
        ]
        for name in COMPARED_FIELDS:
            lines.append(
                f"  {name}: {self.mismatches[name]} discrepancias, "
                f"{self.empty[name]} vacíos capturados")
        lines.append(
            f"CSV: {self.out}" if self.rows else "Sin diferencias: no hay CSV")
        return lines


def snapshot(location, municipality_ids: list) -> dict:
    """Valores respaldables de una ubicación, listos para JSON."""
    values = {name: getattr(location, name) for name in BACKUP_FIELDS}
    values["municipalities"] = sorted(municipality_ids)
    return values


class Filler:
    """Aplica «solo vacíos» sobre todo el universo con geometría.

    Respalda antes de escribir, y por lotes: si el proceso se cae a
    media pasada, lo ya escrito ya está en el archivo.
    """

    def __init__(self, dry_run: bool, limit: int | None, backup: str):
        self.dry_run = dry_run
        self.limit = limit
        self.backup = Path(backup)
        self.seen = 0
        self.touched = 0
        self.by_field: dict[str, int] = {}
        self.entries: list[dict] = []
        self.pending: list[Location] = []
        self.relations: list[Location] = []

    def run(self) -> list[str]:
        universe = located(self.limit, with_relations=True)
        for location in universe.iterator(chunk_size=BATCH_SIZE):
            self.fill(location)
        self.flush()
        return self.report()

    def fill(self, location) -> None:
        self.seen += 1
        previous_ids = [row.pk for row in location.municipalities.all()]
        before = snapshot(location, previous_ids)
        filled = apply_geolocation(
            location, geometry_changed=True, write_relations=False)
        # `None` significa que el motor no llegó a calcular el M2M —una
        # ubicación sin geometría utilizable—, y entonces no hay nada que
        # comparar ni que reescribir.
        crossed = getattr(location, "crossed_municipalities", None)
        after = snapshot(
            location, previous_ids if crossed is None else crossed)
        if after["municipalities"] != before["municipalities"]:
            filled = filled + ["municipalities"]
            self.relations.append(location)
        if not filled:
            return
        self.touched += 1
        for name in filled:
            self.by_field[name] = self.by_field.get(name, 0) + 1
        self.entries.append(
            {"id": location.pk, "before": before, "after": after})
        self.pending.append(location)
        if len(self.pending) >= BATCH_SIZE:
            self.flush()

    def flush(self) -> None:
        if self.dry_run or not self.pending:
            self.pending, self.relations = [], []
            return
        self.write_backup()
        Location.objects.bulk_update(
            self.pending, UPDATED_FIELDS, batch_size=BATCH_SIZE)
        for location in self.relations:
            location.municipalities.set(location.crossed_municipalities)
        self.pending, self.relations = [], []

    def write_backup(self) -> None:
        """Reescribe el archivo completo, que así siempre es JSON válido."""
        self.backup.parent.mkdir(parents=True, exist_ok=True)
        self.backup.write_text(
            json.dumps(self.entries, ensure_ascii=False, indent=1),
            encoding="utf-8")

    def report(self) -> list[str]:
        prefix = "[dry-run] " if self.dry_run else ""
        lines = [
            f"{prefix}Ubicaciones con geometría: {self.seen}",
            f"{prefix}Ubicaciones modificadas: {self.touched}",
        ]
        for name, count in sorted(self.by_field.items()):
            lines.append(f"  {name}: {count}")
        lines.append(
            f"{prefix}Respaldo: {self.backup}" if not self.dry_run
            else "[dry-run] Sin respaldo: no se escribió nada")
        return lines


class Reverter:
    """Devuelve a cada ubicación los valores previos que guardó `--fill`."""

    def __init__(self, backup: str):
        self.backup = Path(backup)
        self.restored = 0
        self.missing = 0
        self.drifted = 0

    def run(self) -> list[str]:
        entries = self.read()
        by_id = {entry["id"]: entry for entry in entries}
        ids = sorted(by_id)
        for start in range(0, len(ids), BATCH_SIZE):
            self.restore(by_id, ids[start:start + BATCH_SIZE])
        self.missing = len(ids) - self.restored
        return self.report()

    def read(self) -> list[dict]:
        try:
            return json.loads(self.backup.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise CommandError(
                f"No se pudo leer el respaldo {self.backup}: {error}"
            ) from error

    def restore(self, by_id: dict, ids: list) -> None:
        rows = list(
            Location.objects.filter(pk__in=ids)
            .prefetch_related("municipalities"))
        for location in rows:
            entry = by_id[location.pk]
            current = snapshot(
                location, [row.pk for row in location.municipalities.all()])
            if current != entry["after"]:
                self.drifted += 1
            for name in BACKUP_FIELDS:
                setattr(location, name, entry["before"][name])
        Location.objects.bulk_update(rows, UPDATED_FIELDS,
                                     batch_size=BATCH_SIZE)
        for location in rows:
            location.municipalities.set(
                by_id[location.pk]["before"]["municipalities"])
        self.restored += len(rows)

    def report(self) -> list[str]:
        lines = [
            f"Respaldo: {self.backup}",
            f"Ubicaciones restauradas: {self.restored}",
        ]
        if self.missing:
            lines.append(f"Ya no existen en la base: {self.missing}")
        if self.drifted:
            lines.append(
                f"Editadas después del backfill (se restauraron igual): "
                f"{self.drifted}")
        return lines
