"""Carga los polígonos del Marco Geoestadístico del INEGI a la base.

Lee `00ent.shp` (estados), `00mun.shp` (municipios) y `00l.shp`
(localidades amanzanadas) con `pyogrio.raw` —`read_dataframe` pediría
geopandas, que el proyecto no instala—, simplifica cada polígono y
guarda su WKB en EPSG:6372.
"""

from django.core.management.base import BaseCommand, CommandError
from shapely import union_all
from shapely import wkb as shapely_wkb

from space_time.models import (
    Locality, LocalityGeometry, Municipality,
    MunicipalityGeometry, State, StateGeometry)

GEO_DIR = "space_time/geo_files"


class Command(BaseCommand):
    help = "Carga los polígonos de entidades, municipios y localidades"

    def add_arguments(self, parser):
        parser.add_argument(
            "--simplify", type=float,
            help="Tolerancia en metros; sin ella, la propia de cada capa")
        parser.add_argument(
            "--layer", choices=["state", "municipality", "locality"],
            help="Cargar solo una de las tres capas")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Solo reporta qué haría, sin escribir")

    def handle(self, *args, **options):
        layers = [options["layer"]] if options["layer"] else [
            "state", "municipality", "locality"]
        for layer in layers:
            simplify = options["simplify"] or SIMPLIFY_M_BY_LAYER[layer]
            loader = LoadGeometries(layer, simplify, options["dry_run"])
            for line in loader.run():
                self.stdout.write(line)


# Medido sobre el Marco 2024: por debajo de esto ningún polígono de la capa
# pierde más de 1 % de área.
SIMPLIFY_M_BY_LAYER = {"state": 50, "municipality": 20, "locality": 10}


class LoadGeometries:
    """Upsert de una capa por su clave INEGI completa."""

    LAYERS = {
        "state": {
            "file": "00ent.shp",
            "model": StateGeometry,
            "target": "state",
            "label": "entidades",
        },
        "municipality": {
            "file": "00mun.shp",
            "model": MunicipalityGeometry,
            "target": "municipality",
            "label": "municipios",
        },
        "locality": {
            "file": "00l.shp",
            "model": LocalityGeometry,
            "target": "locality",
            "label": "localidades",
        },
    }

    def __init__(self, layer: str, simplify: float, dry_run: bool):
        self.layer = self.LAYERS[layer]
        self.simplify = simplify
        self.dry_run = dry_run
        self.created = 0
        self.updated = 0
        self.total_bytes = 0
        self.unmatched: list[str] = []

    def run(self) -> list[str]:
        codes = self.database_codes()
        # Agrupar y fusionar es defensivo, por si una capa trajera
        # varias piezas para la misma clave; en el Marco 2024 la capa
        # 00l trae exactamente un polígono por localidad.
        grouped: dict[int, list] = {}
        for code, geometry in self.read_layer():
            target_id = codes.get(code)
            if target_id is None:
                self.unmatched.append(code)
                continue
            simplified = geometry.simplify(self.simplify)
            if not simplified.is_empty:
                grouped.setdefault(target_id, []).append(simplified)
        rows = []
        for target_id, parts in grouped.items():
            merged = parts[0] if len(parts) == 1 else union_all(parts)
            payload = shapely_wkb.dumps(merged)
            self.total_bytes += len(payload)
            rows.append((target_id, payload))
        self.upsert(rows)
        return self.report()

    def read_layer(self):
        """`(clave completa, geometría)` de cada feature del shapefile."""
        from pyogrio.raw import read

        path = f"{GEO_DIR}/{self.layer['file']}"
        try:
            meta, _, geometries, fields = read(path)
        except Exception as error:
            raise CommandError(
                f"No se pudo leer {path}: {error}. Corre primero "
                f"{GEO_DIR}/download_inegi.sh") from error
        if not str(meta.get("crs", "")).endswith("6372"):
            raise CommandError(
                f"{path} no está en EPSG:6372 sino en {meta.get('crs')}; "
                "el motor de geolocalización espera metros.")
        columns = {name: index for index, name in enumerate(meta["fields"])}
        for position, raw in enumerate(geometries):
            if raw is None:
                continue
            code = self.complete_code(fields, columns, position)
            try:
                geometry = shapely_wkb.loads(bytes(raw))
            except Exception:
                self.unmatched.append(f"{code} (WKB ilegible)")
                continue
            yield code, geometry

    def complete_code(self, fields, columns: dict, position: int) -> str:
        target = self.layer["target"]
        code = fields[columns["CVE_ENT"]][position]
        if target == "state":
            return code
        code = f"{code}-{fields[columns['CVE_MUN']][position]}"
        if target == "municipality":
            return code
        return f"{code}-{fields[columns['CVE_LOC']][position]}"

    def database_codes(self) -> dict[str, int]:
        target = self.layer["target"]
        if target == "state":
            return dict(State.objects.values_list("inegi_code", "id"))
        model = Municipality if target == "municipality" else Locality
        return dict(model.objects.values_list("complete_code", "id"))

    def upsert(self, rows: list) -> None:
        model = self.layer["model"]
        target = self.layer["target"]
        existing = dict(model.objects.values_list(f"{target}_id", "id"))
        to_create, to_update = [], []
        for target_id, payload in rows:
            values = {"wkb": payload, "simplified_m": int(self.simplify)}
            row_id = existing.get(target_id)
            if row_id is None:
                to_create.append(
                    model(**{f"{target}_id": target_id}, **values))
            else:
                to_update.append(model(id=row_id, **{
                    f"{target}_id": target_id}, **values))
        self.created = len(to_create)
        self.updated = len(to_update)
        if self.dry_run:
            return
        model.objects.bulk_create(to_create, batch_size=200)
        model.objects.bulk_update(
            to_update, ["wkb", "simplified_m"], batch_size=200)

    def report(self) -> list[str]:
        prefix = "[dry-run] " if self.dry_run else ""
        label = self.layer["label"]
        megabytes = self.total_bytes / 1024 / 1024
        lines = [
            f"{prefix}Geometrías de {label}: {self.created} creadas, "
            f"{self.updated} actualizadas",
            f"{prefix}WKB simplificado a {self.simplify:g} m: "
            f"{self.total_bytes:,} bytes ({megabytes:.1f} MB)",
        ]
        if self.unmatched:
            lines.append(
                f"Sin fila en la base ({len(self.unmatched)}): "
                + ", ".join(self.unmatched[:20]))
        return lines
