"""Deriva estado, municipio y localidad de una geometría de `Location`.

Lee la cartografía que `load_geometries` dejó en `StateGeometry`,
`MunicipalityGeometry` y `LocalityGeometry`: polígonos del INEGI
simplificados según la capa (50/20/10 m), guardados como WKB en
EPSG:6372, el CRS métrico nativo del INEGI. Todo el cálculo ocurre en
metros; solo la entrada (geojson en EPSG:4326) y el centroide de salida
se reproyectan.

Los índices se cachean por proceso con `functools.lru_cache` y no se
invalidan: recargar la cartografía exige reiniciar el proceso, o llamar
a `clear_indexes` (lo que hacen los tests).

Reglas por tipo de geometría: docs `adr-0026` y `task-39`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from pyproj import Transformer
from shapely import wkb as shapely_wkb
from shapely.geometry import Point, shape
from shapely.ops import transform as shapely_transform
from shapely.strtree import STRtree
from shapely import line_interpolate_point

# CRS de la cartografía del INEGI (Cónica Conforme de Lambert, metros).
CRS_METERS = "EPSG:6372"
CRS_LATLON = "EPSG:4326"

# Un trazo «atraviesa» un municipio si la parte que cae dentro mide más
# que esto. Los umbrales descartan el roce de frontera —dos polígonos
# vecinos comparten el borde y toda línea que lo cruza toca ambos— sin
# perder cruces reales: 50 m es menor que la cuadra urbana más corta y
# 1 ha (10,000 m²) es menor que cualquier predio que el OCSA registre.
MIN_CROSSING_LENGTH_M = 50.0
MIN_CROSSING_AREA_M2 = 10_000.0

# Radio en el que una localidad **sin polígono** cuenta como «tocada»
# por un trazo: es el orden de magnitud del casco de una localidad que el
# INEGI representa con un solo punto. Las que sí tienen polígono se
# miden por intersección directa, sin margen.
LOCALITY_BUFFER_M = 500.0


@dataclass
class PointResolution:
    state: object | None = None
    municipality: object | None = None
    locality: object | None = None


@dataclass
class GeometryResolution:
    """Reglas por tipo de geometría: docs `adr-0026` y `task-39`."""

    municipalities: list = field(default_factory=list)
    single_municipality: object | None = None
    locality: object | None = None
    nearby_localities: int | None = None
    centroid: tuple | None = None


# --- proyección ------------------------------------------------------------

@lru_cache(maxsize=2)
def _transformer(source: str, target: str) -> Transformer:
    return Transformer.from_crs(source, target, always_xy=True)


def to_meters(geometry):
    """Proyecta una geometría de shapely de EPSG:4326 a EPSG:6372."""
    return shapely_transform(
        _transformer(CRS_LATLON, CRS_METERS).transform, geometry)


def to_latlon(geometry):
    """Proyecta una geometría de shapely de EPSG:6372 a EPSG:4326."""
    return shapely_transform(
        _transformer(CRS_METERS, CRS_LATLON).transform, geometry)


def point_in_meters(latitude: float, longitude: float) -> Point:
    x, y = _transformer(CRS_LATLON, CRS_METERS).transform(
        longitude, latitude)
    return Point(x, y)


def feature_to_shape(feature: dict):
    """Geometría de shapely, en metros, de un Feature del contrato.

    Devuelve `None` si el geojson no trae geometría utilizable.
    """
    if not feature:
        return None
    geometry = feature.get("geometry") if feature.get("type") else feature
    if not geometry or not geometry.get("coordinates"):
        return None
    try:
        return to_meters(shape(geometry))
    except Exception:
        return None


# --- índices ---------------------------------------------------------------

@lru_cache(maxsize=1)
def _state_index() -> tuple:
    """`(STRtree, [State, ...], [polígono, ...])` con los 32 estados."""
    from space_time.models import StateGeometry

    rows = list(
        StateGeometry.objects.select_related("state").only("wkb", "state"))
    return _build_index(rows, "state")


@lru_cache(maxsize=64)
def _municipality_index(state_id: int) -> tuple:
    """`(STRtree, [Municipality, ...], [polígono, ...])` de un estado."""
    from space_time.models import MunicipalityGeometry

    rows = list(
        MunicipalityGeometry.objects
        .filter(municipality__state_id=state_id)
        .select_related("municipality__state"))
    return _build_index(rows, "municipality")


def _build_index(rows: list, attribute: str) -> tuple:
    shapes, objects = [], []
    for row in rows:
        try:
            geometry = shapely_wkb.loads(bytes(row.wkb))
        except Exception:
            continue
        if geometry.is_empty:
            continue
        shapes.append(geometry)
        objects.append(getattr(row, attribute))
    if not shapes:
        return None, [], []
    return STRtree(shapes), objects, shapes


@lru_cache(maxsize=None)
def _locality_index(municipality_id: int) -> tuple:
    """`(STRtree, [Locality, ...], [polígono, ...])` amanzanadas."""
    from space_time.models import LocalityGeometry

    rows = list(
        LocalityGeometry.objects
        .filter(locality__municipality_id=municipality_id)
        .select_related("locality"))
    return _build_index(rows, "locality")


def clear_indexes() -> None:
    """Vacía la caché de índices (tests y recargas de cartografía)."""
    _state_index.cache_clear()
    _municipality_index.cache_clear()
    _locality_index.cache_clear()
    _locality_points.cache_clear()


def _query(index: tuple, geometry, predicate: str | None = None) -> list:
    """Pares `(objeto, geometría)` que el índice devuelve para el filtro."""
    tree, objects, shapes = index
    if tree is None:
        return []
    hits = tree.query(geometry, predicate=predicate)
    return [(objects[position], shapes[position]) for position in hits]


# --- resolución ------------------------------------------------------------

def resolve_point(latitude: float, longitude: float,
                  state_id: int | None = None) -> PointResolution:
    """Estado, municipio y localidad que corresponden a un par de grados.

    El `state_id` capturado se prueba primero: si el punto cae dentro se
    ahorra la consulta al índice estatal. Si no cae, se resuelve el
    estado por polígono y se reintenta.
    """
    point = point_in_meters(latitude, longitude)
    municipality = None
    if state_id:
        municipality = _municipality_at(point, state_id)
    state = None
    if municipality is None:
        state = _state_at(point)
        if state is not None:
            municipality = _municipality_at(point, state.pk)
    if municipality is not None:
        state = municipality.state
    return PointResolution(
        state, municipality, _locality_for_point(point, municipality))


def _state_at(point: Point):
    hits = _query(_state_index(), point, "intersects")
    return hits[0][0] if hits else None


def _municipality_at(point: Point, state_id: int):
    hits = _query(_municipality_index(state_id), point, "intersects")
    return hits[0][0] if hits else None


@lru_cache(maxsize=None)
def _locality_points(municipality_id: int) -> tuple:
    """`((Locality, Point), ...)` vigentes del municipio, en metros.

    Se cachea porque el backfill recorre miles de ubicaciones y muchas
    caen en el mismo municipio; sin caché sería una consulta por fila.
    """
    from space_time.models import Locality

    rows = Locality.objects.filter(
        municipality_id=municipality_id, is_current=True,
        latitude__isnull=False, longitude__isnull=False)
    return tuple(
        (locality, point_in_meters(locality.latitude, locality.longitude))
        for locality in rows)


def _locality_for_point(point: Point, municipality):
    """Localidad de un punto: primero por polígono, luego por cercanía.

    El vecino más cercano solo se usa cuando el punto no cae en ninguna
    localidad amanzanada: en una mancha urbana grande, que el INEGI
    también representa con un punto único en el centro, la localidad
    rural de al lado suele quedar más cerca que ese centro.
    """
    if municipality is None:
        return None
    inside = _query(_locality_index(municipality.pk), point, "intersects")
    if inside:
        return inside[0][0]
    candidates = _locality_points(municipality.pk)
    if not candidates:
        return None
    return min(candidates, key=lambda pair: point.distance(pair[1]))[0]


def resolve_geometry(feature: dict,
                     state_id: int | None = None) -> GeometryResolution:
    """Municipios atravesados, localidad y centroide de un trazo."""
    geometry = feature_to_shape(feature)
    if geometry is None or geometry.is_empty:
        return GeometryResolution()
    crossed = _crossed_municipalities(geometry, state_id)
    municipalities = [municipality for municipality, _ in crossed]
    single = municipalities[0] if len(municipalities) == 1 else None
    localities = _localities_near(geometry, municipalities)
    locality = localities[0] if len(localities) == 1 else None
    return GeometryResolution(
        municipalities=[(municipality, measure)
                        for municipality, measure in crossed],
        single_municipality=single,
        locality=locality,
        nearby_localities=len(localities),
        centroid=_centroid(geometry),
    )


def _crossed_municipalities(geometry, state_id: int | None) -> list:
    """`[(Municipality, medida), ...]` ordenado de mayor a menor medida.

    Los candidatos salen del índice estatal (por caja envolvente) y no
    del `state_id` capturado: un trazo puede cruzar la frontera estatal
    y el capturado puede estar mal.
    """
    state_ids = {state.pk for state, _ in _query(_state_index(), geometry)}
    if state_id:
        state_ids.add(state_id)
    crossed = []
    for candidate_state in state_ids:
        for municipality, polygon in _query(
                _municipality_index(candidate_state), geometry):
            measure = _crossing_measure(geometry, polygon)
            if measure is not None:
                crossed.append((municipality, measure))
    crossed.sort(key=lambda pair: pair[1], reverse=True)
    return crossed


def _crossing_measure(geometry, polygon) -> float | None:
    """Área o longitud de la intersección, si pasa el umbral que le toca.

    El umbral lo decide la geometría de la ubicación, no la de la pieza:
    un polígono que solo colinda con el municipio lo corta en una línea
    de borde, y medir esa línea por longitud la daría por atravesada.
    """
    try:
        piece = geometry.intersection(polygon)
    except Exception:
        return None
    if piece.is_empty:
        return None
    if geometry.area > 0:
        return piece.area if piece.area >= MIN_CROSSING_AREA_M2 else None
    return piece.length if piece.length >= MIN_CROSSING_LENGTH_M else None


def _localities_near(geometry, municipalities: list) -> list:
    """Localidades que toca el trazo, dentro de los municipios cruzados.

    La localidad amanzanada cuenta si su polígono corta el trazo; la que
    solo tiene punto de catálogo, si ese punto cae en el buffer. Una
    localidad con polígono nunca se mide por su punto: el polígono ya
    dio la respuesta.
    """
    if not municipalities:
        return []
    from space_time.models import Locality

    area = geometry.buffer(LOCALITY_BUFFER_M)
    touched, mapped = [], set()
    for municipality in municipalities:
        index = _locality_index(municipality.pk)
        mapped.update(locality.pk for locality in index[1])
        touched.extend(
            locality
            for locality, _ in _query(index, geometry, "intersects"))
    rows = Locality.objects.filter(
        municipality__in=municipalities, is_current=True,
        latitude__isnull=False, longitude__isnull=False)
    for locality in rows:
        if locality.pk in mapped:
            continue
        point = point_in_meters(locality.latitude, locality.longitude)
        if area.contains(point):
            touched.append(locality)
    return touched


def _centroid(geometry) -> tuple | None:
    """`(lat, lon)` representativo del trazo.

    La línea usa su punto medio y no el centroide: el centroide de una
    línea curva cae fuera de ella, y el pin del mapa debe estar sobre lo
    dibujado.
    """
    if geometry.is_empty:
        return None
    if geometry.area == 0 and geometry.length > 0:
        middle = line_interpolate_point(geometry, 0.5, normalized=True)
    else:
        middle = geometry.centroid
    if middle.is_empty:
        return None
    point = to_latlon(middle)
    return round(point.y, 6), round(point.x, 6)


# --- aplicación ------------------------------------------------------------

FILLABLE = ("state", "municipality", "locality")


def apply_geolocation(location, geometry_changed: bool = True,
                      write_relations: bool = True) -> list[str]:
    """Escribe en `location` lo derivado y devuelve qué campos tocó.

    No guarda las columnas: quien llama decide entre `save()` y
    `bulk_update`. Tampoco toca `status_location`.

    El M2M se escribe aquí salvo que `write_relations=False`, y en todo
    caso queda en `location.crossed_municipalities`: así el comando de
    backfill puede contarlo sin tocar la base, y diferir la escritura
    hasta después de respaldar lo anterior.
    """
    if location.type_location == "point":
        return _apply_point(location, write_relations)
    return _apply_geometry(location, geometry_changed, write_relations)


def _apply_point(location, write_relations: bool = True) -> list[str]:
    if location.latitude is None or location.longitude is None:
        return []
    resolution = resolve_point(
        location.latitude, location.longitude, location.state_id)
    filled = _fill_empty(location, resolution)
    if location.nearby_localities is not None:
        location.nearby_localities = None
        filled.append("nearby_localities")
    crossed = [location.municipality_id] if location.municipality_id else []
    location.crossed_municipalities = crossed
    if write_relations and location.pk and crossed:
        location.municipalities.set(crossed)
    return filled


def _apply_geometry(location, geometry_changed: bool,
                    write_relations: bool = True) -> list[str]:
    resolution = resolve_geometry(location.geojson, location.state_id)
    if resolution.centroid is None:
        return []
    filled = _fill_empty(
        location, resolution, municipality_from="single")
    if geometry_changed or location.latitude is None:
        latitude, longitude = resolution.centroid
        if (location.latitude, location.longitude) != (latitude, longitude):
            location.latitude = latitude
            location.longitude = longitude
            filled.append("latitude")
            filled.append("longitude")
    if location.nearby_localities != resolution.nearby_localities:
        location.nearby_localities = resolution.nearby_localities
        filled.append("nearby_localities")
    crossed = [municipality.pk
               for municipality, _ in resolution.municipalities]
    location.crossed_municipalities = crossed
    if write_relations and location.pk:
        location.municipalities.set(crossed)
    return filled


def _fill_empty(location, resolution, municipality_from: str = "") -> list[str]:
    municipality = (
        resolution.single_municipality if municipality_from == "single"
        else resolution.municipality)
    values = {
        "state": getattr(resolution, "state", None),
        "municipality": municipality,
        "locality": resolution.locality,
    }
    filled = []
    for name in FILLABLE:
        value = values[name]
        if value is None or getattr(location, f"{name}_id") is not None:
            continue
        setattr(location, name, value)
        filled.append(name)
    # Un municipio recién llenado arrastra su estado, aunque el índice
    # estatal no lo haya resuelto por su cuenta.
    if "municipality" in filled and location.state_id is None:
        location.state = location.municipality.state
        filled.append("state")
    return filled
