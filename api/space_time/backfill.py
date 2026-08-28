"""Revisión y backfill de la geolocalización derivada de las ubicaciones.

Las tres pasadas y todo lo que comparten. `Reviewer` reporta sin
escribir; `Filler` aplica dictámenes y motor, respalda y guarda;
`Reverter` deshace un `--fill` desde ese respaldo. El comando
`geolocate_locations` no hace más que leer argumentos y llamarlas.

`--review` saca un CSV de todas las ubicaciones con proyecto y
geometría —lo capturado contra lo calculado y lo que `--fill` cambiaría
en cada una—, sin escribir; `--fill` aplica «solo vacíos» sobre todo el
universo con geometría; `--revert` deshace un `--fill` a partir del
respaldo que este dejó.

Con dictámenes (`--verdicts`) la misma pasada aplica además lo que un
humano dictaminó sobre los comentarios `YEEKO:` del legado
(`space_time/backfill_verdicts` y docs `task-88`): van antes del motor,
amplían el universo a las ubicaciones dictaminadas aunque no tengan
geometría, y quedan en el mismo respaldo, de modo que un solo
`--revert` deshace las dos cosas.

Nunca llama a `Location.save()`: ese método recalcula el
`status_location` derivado del proyecto, así que sobre un backfill que
no mueve ningún estatus sería un efecto colateral sobre otra entidad
—corregiría en silencio proyectos ya desalineados— más una consulta
extra por fila. Escribe con `bulk_update`.
"""

import csv
import json
from pathlib import Path

from django.core.management.base import CommandError
from django.db.models import Q

from space_time.backfill_verdicts import VerdictApplier, load_verdicts
from space_time.geolocate import apply_geolocation, resolve_geometry, \
    resolve_point
from space_time.geometry import has_geometry, has_geometry_q
from space_time.models import Location

DEFAULT_OUT = ".claude/geolocate_review.csv"
DEFAULT_BACKUP = ".claude/geolocate_fill_{day}.json"
COMPARED_FIELDS = ("state", "municipality", "locality")
DEFAULT_CHANGES = ".claude/geolocate_fill_changes_{day}.csv"
UPDATED_FIELDS = [
    "state", "municipality", "locality", "latitude", "longitude",
    "comments", "details"]
# Lo que el respaldo guarda por ubicación. Son los `_id` y no los
# objetos porque el respaldo es JSON y `--revert` escribe con
# `bulk_update` (nunca `save()`, que recalcularía el `status_location`
# del proyecto). `status_location` no está, y no debe estar: ni el
# backfill ni su reversa mueven el estatus de nadie.
BACKUP_FIELDS = (
    "state_id", "municipality_id", "locality_id", "latitude", "longitude",
    "comments", "details")
# Columnas del CSV de cambios: la revisión de Ricardo es por campo, no
# por ubicación, porque una misma fila mezcla motor y dictamen humano.
CHANGES_FIELDS = ("location_id", "field", "before", "after", "source")
ENGINE = "engine"
# El motor nombra los campos como el modelo (`locality`) y el respaldo
# como la columna (`locality_id`). Se reporta en el vocabulario del
# motor, que es el que ya usan `--review` y `CHANGE_NAMES`.
BACKUP_KEY = {name: f"{name}_id"
              for name in ("state", "municipality", "locality")}
FIELD_NAME = {key: name for name, key in BACKUP_KEY.items()}
BATCH_SIZE = 500
# Campos que el fill tiene prohibido escribir en una ubicación concreta
# porque un humano ya dictaminó lo contrario y el motor no puede saberlo.
# 12716 (Mina El Arco, proyecto 708): el comentario dice que ahí no hay
# ninguna localidad, verificado en QGIS el 2026-08-27; el motor llenaría
# una por vecino más cercano. El municipio sí se puede llenar.
HUMAN_VERDICTS = {12716: ("locality",)}
# Vocabulario de la columna `cambios_fill` del CSV: qué nombre recibe en
# el reporte cada campo que el motor devuelve como tocado. `latitude` y
# `longitude` se mueven juntos y cuentan como un solo cambio.
CHANGE_NAMES = (
    ("state", "estado"),
    ("municipality", "municipio"),
    ("locality", "localidad"),
    ("municipalities", "municipios_atravesados"),
    ("latitude", "centroide"),
)


def located(limit: int | None = None, with_project: bool = False,
            with_relations: bool = False, extra_ids=None):
    """Ubicaciones con geometría, que son las únicas geolocalizables.

    `extra_ids` suma ubicaciones que el motor no puede tocar pero los
    dictámenes sí: el legado dejó comentarios `YEEKO:` en 3 151
    ubicaciones y solo 125 tienen geometría, así que acotar la limpieza
    al universo del motor la volvería casi vacía.
    """
    scope = has_geometry_q()
    if extra_ids:
        scope = scope | Q(pk__in=extra_ids)
    queryset = Location.objects.filter(scope).select_related(
        "state", "municipality", "locality", "project", "status_location")
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


def display_name(entity) -> str:
    """Nombre propio de la entidad, sin la jerarquía que cuelga `__str__`.

    `str(Municipality)` termina en el estado y `str(Locality)` en el
    municipio y el estado; en el CSV cada nivel ya tiene su columna, así
    que el sufijo solo estorba al comparar y al filtrar.
    """
    return getattr(entity, "name", "") or ""


class Reviewer:
    """Reporta el universo revisable entero; no escribe en la base.

    Sale una fila por ubicación con proyecto y geometría, aunque no
    tenga ni diferencias ni cambios: el CSV es el insumo para decidir
    `--fill`, y para eso hace falta ver también lo que no se mueve.
    """

    def __init__(self, out: str, limit: int | None):
        self.out = Path(out)
        self.limit = limit
        self.reviewed = 0
        self.differing = 0
        self.would_change = 0
        self.mismatches = {name: 0 for name in COMPARED_FIELDS}
        self.empty = {name: 0 for name in COMPARED_FIELDS}
        self.rows: list[dict] = []

    def run(self) -> list[str]:
        universe = located(
            self.limit, with_project=True, with_relations=True)
        for location in universe.iterator(chunk_size=BATCH_SIZE):
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
            "status_location": (
                location.status_location.public_name
                if location.status_location_id else ""),
        }
        differing = []
        for name in COMPARED_FIELDS:
            captured = getattr(location, name)
            computed = computed_value(resolution, name)
            row[f"{name}_capturado"] = display_name(captured)
            row[f"{name}_calculado"] = display_name(computed)
            if captured is None:
                self.empty[name] += 1
                if computed is not None:
                    differing.append(name)
            elif computed is not None and computed.pk != captured.pk:
                self.mismatches[name] += 1
                differing.append(name)
        row["municipios_atravesados"] = "; ".join(
            municipality.name
            for municipality, _ in getattr(resolution, "municipalities", []))
        row["diferencias"] = "; ".join(
            label for name, label in CHANGE_NAMES if name in differing)
        # `apply_and_diff` va al final porque escribe sobre el objeto en
        # memoria: las columnas de lo capturado tienen que salir antes.
        changes = change_labels(apply_and_diff(location)[0])
        row["cambios_fill"] = "; ".join(changes)
        row["cambios_fill_n"] = len(changes)
        if changes:
            self.would_change += 1
        if differing:
            self.differing += 1
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
            f"Filas con alguna diferencia: {self.differing}",
            f"Filas que --fill cambiaría: {self.would_change}",
        ]
        for name in COMPARED_FIELDS:
            lines.append(
                f"  {name}: {self.mismatches[name]} discrepancias, "
                f"{self.empty[name]} vacíos capturados")
        lines.append(
            f"CSV: {self.out}" if self.rows else "Universo vacío: no hay CSV")
        return lines


def snapshot(location, municipality_ids: list) -> dict:
    """Valores respaldables de una ubicación, listos para JSON."""
    values = {name: getattr(location, name) for name in BACKUP_FIELDS}
    values["municipalities"] = sorted(municipality_ids)
    return values


def apply_and_diff(location, applier=None) -> tuple:
    """Corre dictámenes y motor en memoria y devuelve qué cambiaría.

    No escribe en la base: `write_relations=False` deja el M2M en
    `crossed_municipalities`. Es la única resolución que existe, y por
    eso la comparten `--review` (que solo la reporta) y `--fill` (que
    además respalda y guarda).

    Los dictámenes van primero para que un municipio recién llenado ya
    esté puesto cuando el motor resuelva la localidad; el motor solo
    corre si hay geometría, porque sin ella no resuelve nada y el
    universo de los dictámenes es mucho más ancho.

    Devuelve `(campos tocados, antes, después, origen por campo)`.
    """
    previous_ids = [row.pk for row in location.municipalities.all()]
    before = snapshot(location, previous_ids)
    sources = applier.apply(location) if applier else {}
    filled = []
    if has_geometry(location):
        filled = apply_geolocation(
            location, geometry_changed=True, write_relations=False)
    filled = honor_human_verdict(location, before, filled)
    # `None` significa que el motor no llegó a calcular el M2M —una
    # ubicación sin geometría utilizable—, y entonces no hay nada que
    # comparar ni que reescribir.
    crossed = getattr(location, "crossed_municipalities", None)
    after = snapshot(location, previous_ids if crossed is None else crossed)
    if after["municipalities"] != before["municipalities"]:
        filled = filled + ["municipalities"]
    touched = [FIELD_NAME.get(key, key) for key in before
               if before[key] != after[key]]
    return sorted(set(filled) | set(touched)), before, after, sources


def honor_human_verdict(location, before: dict,
                        filled: list[str]) -> list[str]:
    """Deshace en memoria lo que `HUMAN_VERDICTS` veta para esa ubicación.

    Se aplica después del motor y no dentro de él: la excepción es del
    backfill sobre filas concretas, no una regla de derivación.
    """
    vetoed = HUMAN_VERDICTS.get(location.pk)
    if not vetoed:
        return filled
    # Gana también sobre los dictámenes de los CSV, no solo sobre el
    # motor: el veredicto humano es el último recurso, no uno más.
    for name in vetoed:
        setattr(location, f"{name}_id", before[f"{name}_id"])
    return [name for name in filled if name not in vetoed]


def change_labels(filled: list[str]) -> list[str]:
    """Traduce los campos tocados al vocabulario del CSV, sin repetir."""
    touched = set(filled)
    return [label for name, label in CHANGE_NAMES if name in touched]


class Filler:
    """Aplica dictámenes y motor sobre el universo que a cada uno toca.

    Respalda antes de escribir, y por lotes: si el proceso se cae a
    media pasada, lo ya escrito ya está en el archivo. `--dry-run` no
    respalda ni escribe, pero sí deja el CSV de cambios, que es el
    artefacto con el que se revisa la pasada antes de correrla de veras.
    """

    def __init__(self, dry_run: bool, limit: int | None, backup: str,
                 verdicts=(), changes: str = ""):
        self.dry_run = dry_run
        self.limit = limit
        self.backup = Path(backup)
        self.changes = Path(changes) if changes else None
        self.verdicts = load_verdicts(verdicts) if verdicts else {}
        self.applier = VerdictApplier(self.verdicts) if self.verdicts else None
        self.sources = [Path(item).name for item in verdicts]
        self.seen = 0
        self.touched = 0
        self.by_field: dict[str, int] = {}
        self.entries: list[dict] = []
        self.pending: list[Location] = []
        self.relations: list[Location] = []
        self.rows: list[dict] = []

    def run(self) -> list[str]:
        universe = located(
            self.limit, with_relations=True, extra_ids=list(self.verdicts))
        for location in universe.iterator(chunk_size=BATCH_SIZE):
            self.fill(location)
        self.flush()
        self.write_changes()
        return self.report()

    def fill(self, location) -> None:
        self.seen += 1
        filled, before, after, sources = apply_and_diff(
            location, self.applier)
        if "municipalities" in filled:
            self.relations.append(location)
        if not filled:
            return
        self.touched += 1
        for name in filled:
            self.by_field[name] = self.by_field.get(name, 0) + 1
        self.record(location, filled, before, after, sources)
        self.entries.append(
            {"id": location.pk, "before": before, "after": after})
        self.pending.append(location)
        if len(self.pending) >= BATCH_SIZE:
            self.flush()

    def record(self, location, filled, before, after, sources) -> None:
        """Una fila del CSV de cambios por campo tocado."""
        for name in filled:
            key = BACKUP_KEY.get(name, name)
            if key not in before:
                continue
            self.rows.append({
                "location_id": location.pk,
                "field": name,
                "before": as_text(before[key]),
                "after": as_text(after[key]),
                "source": sources.get(key, ENGINE),
            })

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

    def write_changes(self) -> None:
        if not self.changes or not self.rows:
            return
        self.changes.parent.mkdir(parents=True, exist_ok=True)
        with self.changes.open(
                "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=CHANGES_FIELDS)
            writer.writeheader()
            writer.writerows(self.rows)

    def report(self) -> list[str]:
        prefix = "[dry-run] " if self.dry_run else ""
        lines = [
            f"{prefix}Ubicaciones recorridas: {self.seen}",
            f"{prefix}Ubicaciones modificadas: {self.touched}",
        ]
        for name, count in sorted(self.by_field.items()):
            lines.append(f"  {name}: {count}")
        lines += self.verdict_report(prefix)
        lines.append(
            f"{prefix}Respaldo: {self.backup}" if not self.dry_run
            else "[dry-run] Sin respaldo: no se escribió nada")
        if self.changes and self.rows:
            lines.append(
                f"{prefix}CSV de cambios: {self.changes} "
                f"({len(self.rows)} filas)")
        return lines

    def verdict_report(self, prefix: str) -> list[str]:
        if not self.applier:
            return []
        lines = []
        for source in self.sources:
            counts = self.applier.counts.get(source)
            lines.append(f"{prefix}Dictámenes de {source}:")
            if not counts:
                lines.append("  (ninguno aplicable)")
                continue
            for name, count in sorted(counts.items()):
                lines.append(f"  {name}: {count}")
        return lines


def as_text(value) -> str:
    """Valor legible en el CSV de cambios; `None` sale como vacío."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value)


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
