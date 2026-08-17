"""Rescata las geometrías de `ocs.ubicaciones` que la migración v1 perdió
o degradó, y normaliza el `geojson` de todas las Location al contrato
vigente (un solo Feature por Location, con geometría Multi* cuando el
original traía varias partes).

Dos fallas del origen justifican el comando:

1. `space_time/migrate/ubicacio.py` compara `type_location` en lugar de
   `ubicacion.tipo_ubicacion`, así que toda Location migrada quedó como
   `point`, incluso las que traían líneas o polígonos.
2. Cuatro ubicaciones con geometría real nunca produjeron Location, y
   dos más fueron redibujadas en el tablero con menos detalle que el
   original.

Es idempotente: cada paso se salta cuando el dato ya está en el estado
destino. Corre en seco por omisión; escribe solo con `--apply`.
"""

import json

from django.core.management.base import BaseCommand
from django.db import transaction

from ocsa_legacy.models import ProyectoToUbicacion, Ubicacion
from project.models import Project
from space_time.models import Location

from space_time.geometry import normalize_geojson


LOST_UBICACIONES = [389, 447, 452, 635]

# Locations redibujadas con menos vértices que el original legacy.
TRUNCATED_REDRAWS = {216: 4434, 226: 12308}

RESTORE_NOTE = (
    "2026-08-17 — Ricardo: se restauró el trazo original del legacy "
    "({before} → {after} vértices) porque el redibujo perdió detalle; "
    "revisar y aprobar de nuevo.")

# El proyecto padre de estas ubicaciones no se puede resolver por
# `proyectos_to_ubicaciones`: su proyecto legacy nunca produjo un Project
# y el equipo volvió a capturarlo a mano en el tablero. La equivalencia
# se estableció por nombre y por coincidencia de estado y municipio.
RECOVERED_PARENTS = {
    447: (
        150,
        "el proyecto legacy 447 duplica en nombre exacto al 7, que sí se "
        "migró como Project 150; la única Location de 150 (14362) cae en "
        "el mismo estado (9) y municipio (279) que la ubicación 447"),
    635: (
        1784,
        "el proyecto legacy 635 «Acueducto Milpillas» no se migró; el "
        "equipo lo recapturó como Project 1784 «Acueducto Milpillas, "
        "Zacatecas», cuya única Location (14333) cae en el mismo estado "
        "(32) y municipio (2439) que la ubicación 635"),
}

LINE_TYPES = {"LineString", "MultiLineString"}
POLYGON_TYPES = {"Polygon", "MultiPolygon"}
POINT_TYPES = {"Point", "MultiPoint"}


def geometry_types(geojson):
    if not geojson:
        return []
    top = geojson.get("type")
    if top == "FeatureCollection":
        return [
            f["geometry"]["type"]
            for f in geojson.get("features", []) if f.get("geometry")]
    if top == "Feature":
        return [geojson["geometry"]["type"]] if geojson.get("geometry") else []
    if "coordinates" in geojson:
        return [top]
    return []


def expected_type_location(types):
    kinds = set(types)
    if not kinds:
        return None
    if kinds <= LINE_TYPES:
        return "line"
    if kinds <= POLYGON_TYPES:
        return "polygon"
    if kinds <= POINT_TYPES:
        return "point"
    return None


def count_vertices(geometry):
    kind = geometry["type"]
    coords = geometry["coordinates"]
    if kind == "Point":
        return 1
    if kind in ("LineString", "MultiPoint"):
        return len(coords)
    if kind in ("MultiLineString", "Polygon"):
        return sum(len(part) for part in coords)
    if kind == "MultiPolygon":
        return sum(len(ring) for poly in coords for ring in poly)
    return 0


def total_vertices(geojson):
    top = geojson.get("type") if geojson else None
    if top == "FeatureCollection":
        return sum(
            count_vertices(f["geometry"])
            for f in geojson.get("features", []) if f.get("geometry"))
    if top == "Feature":
        return count_vertices(geojson["geometry"]) if geojson.get("geometry") \
            else 0
    if geojson and "coordinates" in geojson:
        return count_vertices(geojson)
    return 0


def describe(geojson):
    if not geojson:
        return "None"
    top = geojson.get("type")
    if top == "FeatureCollection":
        inner = ", ".join(
            f"{f['geometry']['type']}({count_vertices(f['geometry'])})"
            for f in geojson.get("features", []) if f.get("geometry"))
        return f"FC[{inner}]"
    if top == "Feature":
        geom = geojson.get("geometry")
        if not geom:
            return "Feature[sin geometría]"
        return f"Feature[{geom['type']}({count_vertices(geom)})]"
    return f"{top}({total_vertices(geojson)})"


def first_point(geojson):
    for geom in _geometries(geojson):
        if geom["type"] == "Point":
            return geom["coordinates"]
        if geom["type"] == "MultiPoint" and geom["coordinates"]:
            return geom["coordinates"][0]
    return None


def _geometries(geojson):
    top = geojson.get("type") if geojson else None
    if top == "FeatureCollection":
        return [
            f["geometry"] for f in geojson.get("features", [])
            if f.get("geometry")]
    if top == "Feature":
        return [geojson["geometry"]] if geojson.get("geometry") else []
    if geojson and "coordinates" in geojson:
        return [geojson]
    return []


def build_lookup_helper():
    """`UbicacionesToLocations.__init__` corre la migración completa, así
    que se construye la instancia sin inicializar y solo se carga el
    índice de estados que necesitan sus buscadores.
    """
    from space_time.migrate.ubicacio import UbicacionesToLocations
    helper = UbicacionesToLocations.__new__(UbicacionesToLocations)
    helper.states = {}
    helper.errors = []
    helper.load_states()
    return helper


class Command(BaseCommand):
    help = (
        "Normaliza el geojson de las Location y recupera las geometrías "
        "legacy perdidas o degradadas por la migración v1.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Escribe los cambios. Sin esta bandera solo simula.")
        parser.add_argument(
            "--dry-run", action="store_true", default=True,
            help="Simulación (comportamiento por omisión).")

    def handle(self, *args, **options):
        self.apply = options["apply"]
        self.decisions = []
        self.summary = {
            "normalized_fc_to_feature": 0,
            "normalized_multi_merge": 0,
            "normalized_bare_geometry": 0,
            "normalized_in_place": 0,
            "type_location_fixed": [],
            "point_in_line_or_polygon": [],
            "geometry_wins_over_latlon": [],
            "restored": [],
            "created": [],
            "skipped": [],
        }
        mode = "APLICANDO CAMBIOS" if self.apply else "SIMULACIÓN (dry-run)"
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"recover_legacy_geoms — {mode}"))
        with transaction.atomic():
            self.step_normalize()
            self.step_restore_truncated()
            self.step_create_lost()
            self.step_report_duplicates()
            if not self.apply:
                transaction.set_rollback(True)

        self.print_summary()

    # ------------------------------------------------------------------
    # Paso 1
    # ------------------------------------------------------------------
    def step_normalize(self):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n[1] Normalización de Location.geojson"))
        query = Location.objects.exclude(geojson=None).order_by("id")
        for loc in query:
            types = geometry_types(loc.geojson)
            if not types:
                self.summary["skipped"].append(
                    (loc.id, "geojson sin geometría"))
                self.stdout.write(
                    f"  Location {loc.id}: sin geometría, se omite")
                continue
            expected = expected_type_location(types)
            if expected is None:
                self.summary["skipped"].append(
                    (loc.id, f"tipos mezclados {sorted(set(types))}"))
                self.stdout.write(self.style.WARNING(
                    f"  Location {loc.id}: tipos mezclados "
                    f"{sorted(set(types))}, se omite"))
                continue

            # Punto guardado en una fila declarada línea/polígono: la
            # geometría no representa la forma prometida, así que baja a
            # punto y viaja en latitude/longitude.
            if expected == "point" and loc.type_location != "point":
                self.handle_point_in_shape_row(loc)
                continue

            changed = []
            if expected != loc.type_location:
                # La geometría manda sobre el catálogo: type_location
                # quedó mal por el bug del migrador, no al revés.
                old = loc.type_location
                loc.type_location = expected
                changed.append(f"type_location {old} → {expected}")
                self.summary["type_location_fixed"].append(
                    (loc.id, old, expected))
                if loc.latitude is not None or loc.longitude is not None:
                    self.summary["geometry_wins_over_latlon"].append(
                        (loc.id, old, expected, loc.latitude, loc.longitude))

            before = loc.geojson
            try:
                after = normalize_geojson(before, loc.type_location)
            except ValueError as exc:
                self.summary["skipped"].append((loc.id, str(exc)))
                self.stdout.write(self.style.WARNING(
                    f"  Location {loc.id}: {exc}, se omite"))
                continue

            if after != before:
                kind = self.classify_normalization(before, after)
                self.summary[kind] += 1
                changed.append(
                    f"geojson {describe(before)} → {describe(after)}")
                loc.geojson = after

            if changed:
                self.stdout.write(
                    f"  Location {loc.id} (ubic {loc.ubicacion_id_ref}): "
                    + "; ".join(changed))
                self.save(loc, ["type_location", "geojson"])

    @staticmethod
    def classify_normalization(before, after):
        top = before.get("type")
        if top not in ("Feature", "FeatureCollection"):
            return "normalized_bare_geometry"
        if top == "FeatureCollection":
            if len(before.get("features", [])) > 1:
                return "normalized_multi_merge"
            return "normalized_fc_to_feature"
        return "normalized_in_place"

    def handle_point_in_shape_row(self, loc):
        point = first_point(loc.geojson)
        old_type = loc.type_location
        parent = self.parent_label(loc)
        self.summary["point_in_line_or_polygon"].append(
            (loc.id, old_type, point, parent))
        self.stdout.write(self.style.WARNING(
            f"  Location {loc.id} ({parent}): {old_type} con geometría "
            f"Point {point} → type_location=point, lat/lon desde el punto, "
            f"geojson=None  [DECISIÓN a validar]"))
        if point:
            loc.longitude, loc.latitude = point[0], point[1]
        loc.geojson = None
        loc.type_location = "point"
        self.save(loc, ["latitude", "longitude", "geojson", "type_location"])

    @staticmethod
    def parent_label(loc):
        if loc.project_id:
            return f"project {loc.project_id}"
        if loc.event_id:
            return f"event {loc.event_id}"
        if loc.impact_id:
            return f"impact {loc.impact_id}"
        return "sin padre"

    # ------------------------------------------------------------------
    # Paso 2
    # ------------------------------------------------------------------
    def step_restore_truncated(self):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n[2] Restauración de redibujos truncados"))
        for ubic_id, loc_id in TRUNCATED_REDRAWS.items():
            loc = Location.objects.filter(pk=loc_id).first()
            if not loc:
                self.summary["skipped"].append(
                    (loc_id, "Location inexistente"))
                continue
            ubicacion = Ubicacion.objects.filter(pk=ubic_id).first()
            legacy = self.parse_geom(ubicacion)
            if not legacy:
                self.summary["skipped"].append(
                    (loc_id, f"ubic {ubic_id} sin geom parseable"))
                continue
            try:
                normalized = normalize_geojson(legacy, loc.type_location)
            except ValueError as exc:
                self.summary["skipped"].append((loc_id, str(exc)))
                continue
            before_n = total_vertices(loc.geojson)
            after_n = total_vertices(normalized)
            if before_n >= after_n:
                self.stdout.write(
                    f"  Location {loc_id} (ubic {ubic_id}): ya tiene "
                    f"{before_n} vértices ≥ {after_n} del legacy, se omite")
                self.summary["skipped"].append(
                    (loc_id, "ya restaurada o con más detalle"))
                continue
            note = RESTORE_NOTE.format(before=before_n, after=after_n)
            old_status = loc.status_location_id
            self.stdout.write(self.style.WARNING(
                f"  Location {loc_id} (ubic {ubic_id}): "
                f"{describe(loc.geojson)} [{before_n} vért.] → "
                f"{describe(normalized)} [{after_n} vért.]; "
                f"status {old_status} → need_consensus"))
            self.stdout.write(f"      nota: {note}")
            loc.geojson = normalized
            expected = expected_type_location(geometry_types(normalized))
            if expected and expected != loc.type_location:
                loc.type_location = expected
            loc.status_location_id = "need_consensus"
            loc.comments = self.append_comment(loc.comments, note)
            self.summary["restored"].append(
                (loc_id, ubic_id, before_n, after_n, old_status))
            self.save(loc, [
                "geojson", "type_location", "status_location", "comments"])

    @staticmethod
    def append_comment(existing, note):
        existing = (existing or "").strip()
        if note in existing:
            return existing
        return f"{existing}\n{note}".strip()

    @staticmethod
    def parse_geom(ubicacion):
        if not ubicacion or not ubicacion.geom:
            return None
        try:
            return json.loads(ubicacion.geom)
        except json.JSONDecodeError:
            return None

    # ------------------------------------------------------------------
    # Paso 3
    # ------------------------------------------------------------------
    def step_create_lost(self):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n[3] Alta de las Location perdidas"))
        helper = None
        for ubic_id in LOST_UBICACIONES:
            existing = Location.objects.filter(ubicacion_id_ref=ubic_id)
            if existing.exists():
                ids = list(existing.values_list("id", flat=True))
                self.stdout.write(
                    f"  ubic {ubic_id}: ya existe Location {ids}, se omite")
                self.summary["skipped"].append(
                    (f"ubic {ubic_id}", "Location ya existe"))
                continue
            ubicacion = Ubicacion.objects.filter(pk=ubic_id).first()
            legacy = self.parse_geom(ubicacion)
            if not legacy:
                self.summary["skipped"].append(
                    (f"ubic {ubic_id}", "geom no parseable"))
                continue
            types = geometry_types(legacy)
            type_location = expected_type_location(types) or "point"
            try:
                geojson = normalize_geojson(legacy, type_location)
            except ValueError as exc:
                self.summary["skipped"].append((f"ubic {ubic_id}", str(exc)))
                continue

            if helper is None:
                helper = build_lookup_helper()
            state_id = helper.get_state_id(ubicacion.estado)
            municipality, mun_count = helper.get_municipality(
                state_id, ubicacion.municipio)
            locality, loc_count = helper.get_locality(
                municipality, ubicacion.localidad)
            comments = []
            if not state_id and ubicacion.estado:
                comments.append(f"Estado no encontrado: {ubicacion.estado}")
            if not municipality and ubicacion.municipio:
                comments.append(
                    f"Municipio no encontrado: {ubicacion.municipio}")
            if not locality and ubicacion.localidad:
                comments.append(
                    f"Localidad no encontrada: {ubicacion.localidad}")
            details = (ubicacion.especificaciones or "").strip()

            project, note = self.resolve_project(ubic_id)
            final_comments = f"YEEKO: {'; '.join(comments)}" if comments \
                else None
            if project and ubic_id in RECOVERED_PARENTS:
                evidence = (
                    f"2026-08-17 — proyecto asignado por equivalencia "
                    f"manual: {note}")
                final_comments = self.append_comment(final_comments, evidence)

            self.stdout.write(
                f"  ubic {ubic_id}: crear Location "
                f"type_location={type_location} {describe(geojson)} "
                f"estado={state_id} municipio="
                f"{municipality.id if municipality else None}"
                f"({mun_count}) localidad="
                f"{locality.id if locality else None}({loc_count}) "
                f"project={project.id if project else None} — {note}")
            if final_comments:
                self.stdout.write(f"      comments: {final_comments}")
            if not project:
                self.decisions.append(
                    f"ubic {ubic_id}: se crea sin padre — {note}")

            self.summary["created"].append(
                (ubic_id, type_location, project.id if project else None,
                 note))
            new_loc = Location(
                project=project,
                state_id=state_id,
                municipality=municipality,
                locality=locality,
                details=details,
                geojson=geojson,
                type_location=type_location,
                ubicacion_id_ref=ubic_id,
                comments=final_comments,
                status_location_id="migrated_v1",
            )
            if self.apply:
                new_loc.save()
                self.stdout.write(self.style.SUCCESS(
                    f"      creada Location {new_loc.id}"))

    def resolve_project(self, ubic_id):
        if ubic_id in RECOVERED_PARENTS:
            project_id, evidence = RECOVERED_PARENTS[ubic_id]
            project = Project.objects.filter(pk=project_id).first()
            if project:
                return project, f"Project {project_id} — {evidence}"
            return None, (
                f"Project {project_id} esperado por equivalencia manual "
                f"pero no existe")
        links = list(ProyectoToUbicacion.objects.filter(ubicacion_id=ubic_id))
        legacy_ids = sorted({lk.proyecto_id for lk in links if lk.proyecto_id})
        if not legacy_ids:
            return None, "sin vínculo en proyectos_to_ubicaciones"
        projects = list(Project.objects.filter(proyecto_id_ref__in=legacy_ids))
        if len(projects) == 1 and len(legacy_ids) == 1:
            return projects[0], f"proyecto legacy {legacy_ids[0]}"
        if not projects:
            return None, (
                f"proyecto(s) legacy {legacy_ids} sin Project migrado")
        return None, (
            f"ambiguo: legacy {legacy_ids} → Projects "
            f"{[p.id for p in projects]}")

    # ------------------------------------------------------------------
    # Paso 4
    # ------------------------------------------------------------------
    def step_report_duplicates(self):
        self.stdout.write(self.style.MIGRATE_HEADING(
            "\n[4] ubicacion_id_ref duplicados (solo reporte)"))
        from collections import Counter
        counter = Counter(
            Location.objects.exclude(ubicacion_id_ref=None)
            .values_list("ubicacion_id_ref", flat=True))
        dups = sorted(ref for ref, n in counter.items() if n > 1)
        if not dups:
            self.stdout.write("  ninguno")
            return
        compared = [
            "state_id", "municipality_id", "locality_id", "latitude",
            "longitude", "geojson", "type_location", "details", "comments",
            "status_location_id", "project_id", "event_id", "impact_id"]
        for ref in dups:
            rows = list(Location.objects.filter(ubicacion_id_ref=ref)
                        .order_by("id"))
            base = {f: getattr(rows[0], f) for f in compared}
            diffs = set()
            for row in rows[1:]:
                for field in compared:
                    if getattr(row, field) != base[field]:
                        diffs.add(field)
            verdict = "idénticas" if not diffs \
                else f"difieren en {sorted(diffs)}"
            self.stdout.write(
                f"  ubic {ref}: Locations "
                f"{[r.id for r in rows]} — {verdict}")
            for row in rows:
                self.stdout.write(
                    f"      {row.id}: {self.parent_label(row)}, "
                    f"type={row.type_location}, estado={row.state_id}, "
                    f"mun={row.municipality_id}, "
                    f"status={row.status_location_id}")

    # ------------------------------------------------------------------
    def save(self, loc, fields):
        if self.apply:
            loc.save(update_fields=fields)

    def print_summary(self):
        s = self.summary
        self.stdout.write(self.style.MIGRATE_HEADING("\n[5] Resumen"))
        self.stdout.write(
            f"  Normalizadas FC-de-1 → Feature: "
            f"{s['normalized_fc_to_feature']}")
        self.stdout.write(
            f"  Normalizadas FC multi → Feature Multi*: "
            f"{s['normalized_multi_merge']}")
        self.stdout.write(
            f"  Normalizadas geometría suelta → Feature: "
            f"{s['normalized_bare_geometry']}")
        self.stdout.write(
            f"  Feature ya normalizado, solo corrección interna "
            f"(orientación de anillos / Z): {s['normalized_in_place']}")
        self.stdout.write(
            f"  type_location corregidos: {len(s['type_location_fixed'])}")
        for loc_id, old, new in s["type_location_fixed"]:
            self.stdout.write(f"      {loc_id}: {old} → {new}")
        self.stdout.write(
            f"  Punto en fila línea/polígono (degradadas a point): "
            f"{len(s['point_in_line_or_polygon'])}")
        for loc_id, old, point, parent in s["point_in_line_or_polygon"]:
            self.stdout.write(f"      {loc_id} ({parent}): {old} → point, "
                              f"punto {point}")
        self.stdout.write(
            f"  Con lat/lon previa que conservan (geometría mandó): "
            f"{len(s['geometry_wins_over_latlon'])}")
        for loc_id, old, new, lat, lon in s["geometry_wins_over_latlon"]:
            self.stdout.write(
                f"      {loc_id}: {old} → {new}, lat/lon {lat}, {lon}")
        self.stdout.write(f"  Restauradas desde legacy: {len(s['restored'])}")
        for loc_id, ubic_id, before, after, old_status in s["restored"]:
            self.stdout.write(
                f"      {loc_id} (ubic {ubic_id}): {before} → {after} vért., "
                f"status {old_status} → need_consensus")
        self.stdout.write(f"  Creadas: {len(s['created'])}")
        for ubic_id, kind, project_id, note in s["created"]:
            self.stdout.write(
                f"      ubic {ubic_id}: {kind}, project={project_id} ({note})")
        self.stdout.write(f"  Omitidas: {len(s['skipped'])}")
        for key, reason in s["skipped"]:
            self.stdout.write(f"      {key}: {reason}")
        if self.decisions:
            self.stdout.write(self.style.WARNING(
                "\n  Decisiones pendientes de validar:"))
            for item in self.decisions:
                self.stdout.write(self.style.WARNING(f"      - {item}"))
        if not self.apply:
            self.stdout.write(self.style.WARNING(
                "\n  Nada se escribió: corre con --apply para aplicar."))
