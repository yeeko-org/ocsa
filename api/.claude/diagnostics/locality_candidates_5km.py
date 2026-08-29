"""Cuántas localidades caben en 5 km de un pin, y qué tan lejos queda el
municipio capturado con tolerancia cero.

Solo lectura: no escribe en la base ni toca ningún modelo. Reutiliza los
índices del motor (`space_time/geolocate.py`) y la medida de
`space_time/far_pins.py`.

    venv/bin/python .claude/diagnostics/locality_candidates_5km.py

Tres bloques:

1. Pines (`type_location="point"` con coordenadas): cuántas localidades
   quedan a 5 km o menos, restringiendo al municipio que resuelve el
   motor y sin restringir a ninguno. La localidad amanzanada se mide
   contra su polígono; la que solo existe como fila del AGEEML, contra su
   punto de catálogo. Se excluyen los marcadores «Ninguno».
2. Pines contra el municipio capturado con tolerancia cero: cuántos se
   salen aunque sea un metro, por tramos de distancia.
3. Trazos (`line`/`polygon` con geojson): cuántas localidades ve la regla
   del motor (`_localities_near`) contra la de 5 km
   (`localities_within`).
"""

import os
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402

django.setup()

from shapely import wkb as shapely_wkb  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402

from space_time.far_pins import municipality_polygon  # noqa: E402
from space_time.geolocate import (  # noqa: E402
    LOCALITY_TOLERANCE_M, APPROXIMATE_STATUS, _catalog_localities,
    _locality_index, _localities_near, feature_to_shape,
    localities_within, point_in_meters, resolve_geometry, resolve_point)
from space_time.models import (  # noqa: E402
    Location, MunicipalityGeometry)

RADIUS_M = LOCALITY_TOLERANCE_M


def national_municipality_index():
    """`(STRtree, [id, ...], [polígono, ...])` con los 2,478 municipios.

    El motor indexa por estado; para la variante sin restricción de
    municipio hace falta el país entero.
    """
    ids, shapes = [], []
    for row in MunicipalityGeometry.objects.only("wkb", "municipality_id"):
        try:
            geometry = shapely_wkb.loads(bytes(row.wkb))
        except Exception:
            continue
        if geometry.is_empty:
            continue
        ids.append(row.municipality_id)
        shapes.append(geometry)
    return STRtree(shapes), ids, shapes


def locality_distances(point, municipality_ids: list) -> dict:
    """`{locality_id: metros}` de las localidades de esos municipios.

    Cada localidad se mide una sola vez y con la referencia que le toca:
    polígono si lo tiene cargado, punto del catálogo si no.
    """
    distances: dict[int, float] = {}
    mapped: set[int] = set()
    municipalities = list(municipality_ids)
    for municipality_id in municipalities:
        tree, localities, polygons = _locality_index(municipality_id)
        for locality, polygon in zip(localities, polygons):
            mapped.add(locality.pk)
            distances[locality.pk] = point.distance(polygon)
    for locality in _catalog_localities(municipalities, mapped):
        reference = point_in_meters(locality.latitude, locality.longitude)
        distances[locality.pk] = point.distance(reference)
    return distances


def bucket(count: int) -> str:
    return "4+" if count >= 4 else str(count)


def summarize(counter: Counter, total: int) -> str:
    parts = []
    for key in ("0", "1", "2", "3", "4+"):
        n = counter.get(key, 0)
        parts.append(
            f"{key}: {n} ({n / total:.1%})" if total else f"{key}: {n}")
    return " | ".join(parts)


def pins() -> None:
    universe = (
        Location.objects
        .filter(type_location="point", latitude__isnull=False,
                longitude__isnull=False)
        .select_related("municipality", "status_location")
        .order_by("id"))
    tree, muni_ids, _ = national_municipality_index()

    engine_counts, free_counts = Counter(), Counter()
    nearest_engine, nearest_free = [], []
    no_municipality = 0
    autofill_total = 0
    autofill_multi = 0
    autofill_none = 0
    seen = 0
    for location in universe.iterator(chunk_size=500):
        seen += 1
        point = point_in_meters(location.latitude, location.longitude)
        resolution = resolve_point(
            location.latitude, location.longitude, location.state_id)
        engine_municipality = resolution.municipality

        # Variante del motor: solo el municipio donde cae el pin.
        if engine_municipality is None:
            no_municipality += 1
            engine_near = {}
        else:
            engine_near = {
                pk: d for pk, d in locality_distances(
                    point, [engine_municipality.pk]).items()
                if d <= RADIUS_M}
        engine_counts[bucket(len(engine_near))] += 1

        # Variante libre: cualquier municipio a 5 km o menos del pin, que
        # es condición necesaria para que alguna de sus localidades lo
        # esté.
        area = point.buffer(RADIUS_M)
        candidates = [muni_ids[i] for i in tree.query(area)]
        free_all = locality_distances(point, candidates)
        free_near = {pk: d for pk, d in free_all.items() if d <= RADIUS_M}
        free_counts[bucket(len(free_near))] += 1
        if free_all:
            nearest_free.append(min(free_all.values()))
        if engine_municipality is not None:
            engine_all = locality_distances(point, [engine_municipality.pk])
            if engine_all:
                nearest_engine.append(min(engine_all.values()))

        # Autollenado: localidad vacía y sin la salvaguarda del
        # «Aprobado (Aproximado)».
        fillable = (location.locality_id is None
                    and location.status_location_id != APPROXIMATE_STATUS)
        if fillable and engine_municipality is not None:
            autofill_total += 1
            if len(engine_near) >= 2:
                autofill_multi += 1
            if not engine_near:
                autofill_none += 1

    print(f"\n=== 1. Localidades a {RADIUS_M:.0f} m de un pin ===")
    print(f"Puntos con coordenadas revisados: {seen}")
    print(f"Pines que no caen en ningún municipio: {no_municipality}")
    print(f"Restringido al municipio del motor: "
          f"{summarize(engine_counts, seen)}")
    print(f"Sin restricción de municipio:       "
          f"{summarize(free_counts, seen)}")
    for label, values in (("dentro del municipio", nearest_engine),
                          ("sin restricción", nearest_free)):
        if not values:
            continue
        ordered = sorted(values)
        print(f"Distancia a la localidad más cercana, {label} "
              f"(n={len(ordered)}): mediana "
              f"{statistics.median(ordered):,.0f} m, "
              f"media {statistics.fmean(ordered):,.0f} m, "
              f"p75 {ordered[int(len(ordered) * 0.75)]:,.0f} m, "
              f"p90 {ordered[int(len(ordered) * 0.90)]:,.0f} m, "
              f"p99 {ordered[int(len(ordered) * 0.99)]:,.0f} m, "
              f"máx {ordered[-1]:,.0f} m")
        print(f"  a más de {RADIUS_M:.0f} m: "
              f"{sum(1 for d in ordered if d > RADIUS_M)}; "
              f"exactamente 0 m (el pin cae dentro de la mancha): "
              f"{sum(1 for d in ordered if d == 0)}")
    print(f"Pines que el motor autollenaría (localidad vacía, no "
          f"aproximado, con municipio resuelto): {autofill_total}")
    print(f"  de esos, con 2 o más candidatas a {RADIUS_M:.0f} m: "
          f"{autofill_multi}")
    print(f"  de esos, con la más cercana a más de {RADIUS_M:.0f} m: "
          f"{autofill_none}")


PIN_BUCKETS = (
    ("0 m (dentro)", 0.0),
    ("(0, 20 m]", 20.0),
    ("(20 m, 100 m]", 100.0),
    ("(100 m, 500 m]", 500.0),
    ("(500 m, 2 km]", 2_000.0),
    ("> 2 km", float("inf")),
)


def far_pins_zero() -> None:
    universe = (
        Location.objects
        .filter(type_location="point", project__isnull=False,
                latitude__isnull=False, longitude__isnull=False,
                municipality__isnull=False)
        .order_by("id"))
    counts = Counter()
    seen = 0
    unmeasurable = 0
    for location in universe.iterator(chunk_size=500):
        polygon = municipality_polygon(location.municipality_id)
        if polygon is None:
            unmeasurable += 1
            continue
        seen += 1
        point = point_in_meters(location.latitude, location.longitude)
        distance = point.distance(polygon)
        for label, ceiling in PIN_BUCKETS:
            if distance <= ceiling:
                counts[label] += 1
                break
    print("\n=== 2. Pin contra municipio capturado, tolerancia cero ===")
    print(f"Puntos con proyecto, coordenadas y municipio: {seen}"
          + (f" ({unmeasurable} sin polígono)" if unmeasurable else ""))
    outside = seen - counts.get("0 m (dentro)", 0)
    print(f"Fuera del polígono aunque sea un metro: {outside} "
          f"({outside / seen:.1%})" if seen else "")
    for label, _ in PIN_BUCKETS:
        n = counts.get(label, 0)
        print(f"  {label}: {n}" + (f" ({n / seen:.1%})" if seen else ""))


def traces() -> None:
    universe = (
        Location.objects
        .filter(type_location__in=("line", "polygon"), geojson__isnull=False)
        .order_by("id"))
    engine_counts, wide_counts = Counter(), Counter()
    seen = 0
    no_municipality = 0
    for location in universe.iterator(chunk_size=500):
        geometry = feature_to_shape(location.geojson)
        if geometry is None or geometry.is_empty:
            continue
        seen += 1
        resolution = resolve_geometry(location.geojson, location.state_id)
        municipalities = [m for m, _ in resolution.municipalities]
        if not municipalities:
            no_municipality += 1
        engine = _localities_near(geometry, municipalities)
        wide = localities_within(geometry, municipalities, RADIUS_M)
        engine_counts[bucket(len(engine))] += 1
        wide_counts[bucket(len(wide))] += 1
    print("\n=== 3. Trazo y localidad: contacto del motor contra 5 km ===")
    print(f"Trazos con geojson utilizable: {seen} "
          f"({no_municipality} sin municipio atravesado)")
    print(f"Regla del motor (_localities_near): "
          f"{summarize(engine_counts, seen)}")
    print(f"Regla de {RADIUS_M / 1000:.0f} km (localities_within): "
          f"{summarize(wide_counts, seen)}")


def main() -> None:
    pins()
    far_pins_zero()
    traces()


if __name__ == "__main__":
    main()
