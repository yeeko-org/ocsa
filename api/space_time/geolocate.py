"""Deriva estado, municipio y localidad de una geometría de `Location`.

Reglas, umbrales y contratos: skill `ocs-geo` y docs `adr-0026`.

Los índices se cachean por proceso con `functools.lru_cache` y no se
invalidan: recargar la cartografía exige reiniciar el proceso, o llamar
a `clear_indexes` (lo que hacen los tests).
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

# Metros: 50 m es menor que la cuadra urbana más corta.
MIN_CROSSING_LENGTH_M = 50.0
# Metros cuadrados: 1 ha es menor que cualquier predio que el OCSA registre.
MIN_CROSSING_AREA_M2 = 10_000.0

# Metros: margen para las localidades sin polígono, que el INEGI
# representa con un solo punto.
LOCALITY_BUFFER_M = 500.0

# Metros: hasta dónde se da por buena la localidad capturada de un trazo
# o de un pin. Vive aquí, y no en `far_pins`/`off_traces`, para que la
# marca editorial y el aviso en vivo del editor usen el mismo número.
# Decidido por Ricardo el 2026-08-28.
LOCALITY_TOLERANCE_M = 5_000.0

# El AGEEML usa «Ninguno» como marcador de localidad sin nombre, no como
# topónimo: son 1,610 filas del catálogo, casi todas ranchos y predios
# sueltos. Ninguna ubicación debe recibir una de ellas como localidad.
PLACEHOLDER_LOCALITY_NAMES = ("Ninguno",)


def without_placeholders(queryset, field: str = "name"):
    """Quita del queryset las localidades marcador del AGEEML."""
    return queryset.exclude(
        **{f"{field}__in": PLACEHOLDER_LOCALITY_NAMES})


@dataclass
class PointResolution:
    state: object | None = None
    municipality: object | None = None
    locality: object | None = None


@dataclass
class GeometryResolution:
    municipalities: list = field(default_factory=list)
    single_municipality: object | None = None
    # Todas las que toca el trazo; `locality` solo se llena cuando es una
    # sola, porque el motor no elige entre varias.
    localities: list = field(default_factory=list)
    locality: object | None = None
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

    rows = list(without_placeholders(
        LocalityGeometry.objects
        .filter(locality__municipality_id=municipality_id,
                locality__is_current=True)
        .select_related("locality"), "locality__name"))
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

    rows = without_placeholders(Locality.objects.filter(
        municipality_id=municipality_id, is_current=True,
        latitude__isnull=False, longitude__isnull=False))
    return tuple(
        (locality, point_in_meters(locality.latitude, locality.longitude))
        for locality in rows)


def _locality_for_point(point: Point, municipality):
    """Localidad de un punto: primero por polígono, luego por cercanía.

    La cercanía es solo respaldo: en una mancha urbana que el INEGI
    representa con un punto único al centro, la localidad rural de al
    lado suele quedar más cerca que ese centro. Y solo hasta
    `LOCALITY_TOLERANCE_M`: en un municipio despoblado la más cercana
    puede estar a decenas de kilómetros, y escribirla sería inventar el
    sitio en vez de derivarlo.
    """
    if municipality is None:
        return None
    inside = _query(_locality_index(municipality.pk), point, "intersects")
    if inside:
        return inside[0][0]
    candidates = _locality_points(municipality.pk)
    if not candidates:
        return None
    locality, reference = min(
        candidates, key=lambda pair: point.distance(pair[1]))
    if point.distance(reference) > LOCALITY_TOLERANCE_M:
        return None
    return locality


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
        localities=localities,
        locality=locality,
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


def _catalog_localities(municipalities: list, mapped: set):
    """Localidades vigentes con coordenadas y sin polígono cargado.

    `mapped` trae las que sí tienen `LocalityGeometry`: una localidad con
    polígono nunca se mide por su punto, porque el polígono ya dio la
    respuesta.
    """
    from space_time.models import Locality

    rows = without_placeholders(Locality.objects.filter(
        municipality__in=municipalities, is_current=True,
        latitude__isnull=False, longitude__isnull=False))
    return [locality for locality in rows if locality.pk not in mapped]


def _localities_near(geometry, municipalities: list) -> list:
    """Localidades que toca el trazo, dentro de los municipios cruzados.

    Es el criterio del **motor**, del que sale el autollenado de
    `locality` (docs `adr-0026`): la localidad amanzanada cuenta solo si
    su polígono corta el trazo, y la que solo tiene punto de catálogo,
    si ese punto cae en el buffer de `LOCALITY_BUFFER_M`. La tolerancia
    más ancha de la revisión editorial es otra función,
    `localities_within`, y no toca esta.
    """
    if not municipalities:
        return []
    touched, mapped = [], set()
    for municipality in municipalities:
        index = _locality_index(municipality.pk)
        mapped.update(locality.pk for locality in index[1])
        touched.extend(
            locality
            for locality, _ in _query(index, geometry, "intersects"))
    area = geometry.buffer(LOCALITY_BUFFER_M)
    touched.extend(
        locality for locality in _catalog_localities(municipalities, mapped)
        if area.contains(
            point_in_meters(locality.latitude, locality.longitude)))
    return touched


def localities_within(geometry, municipalities: list,
                      buffer_m: float = LOCALITY_TOLERANCE_M) -> list:
    """`[(Locality, metros), ...]` a `buffer_m` o menos, de más cerca a
    más lejos.

    Mide por distancia, no por contacto, y con el mismo criterio que
    `far_pins` usa para el pin: la amanzanada contra su polígono, la que
    solo existe como fila del AGEEML contra su punto de catálogo. Es lo
    que consume el endpoint para avisar en vivo, con la tolerancia de
    `LOCALITY_TOLERANCE_M`; el autollenado del motor sigue por
    `_localities_near`.

    Sirve igual a un punto que a un trazo: la distancia de shapely no
    distingue, y el aviso del editor es el mismo en los dos casos.
    """
    if not municipalities or geometry is None or geometry.is_empty:
        return []
    area = geometry.buffer(buffer_m)
    near, mapped = [], set()
    for municipality in municipalities:
        index = _locality_index(municipality.pk)
        mapped.update(locality.pk for locality in index[1])
        for locality, polygon in _query(index, area):
            distance = geometry.distance(polygon)
            if distance <= buffer_m:
                near.append((locality, distance))
    for locality in _catalog_localities(municipalities, mapped):
        distance = geometry.distance(
            point_in_meters(locality.latitude, locality.longitude))
        if distance <= buffer_m:
            near.append((locality, distance))
    near.sort(key=lambda pair: pair[1])
    return near


def locality_points(localities: list) -> dict:
    """`{id: [lon, lat]}` con qué se dibuja cada localidad en el mapa.

    El centroide del polígono para la amanzanada y el punto del catálogo
    AGEEML para la que no lo tiene. Es dónde ponerle la etiqueta, no
    contra qué se midió: la distancia de la amanzanada va contra todo su
    polígono, así que un pin dentro de la mancha marca 0 km aunque el
    centroide quede a kilómetros.
    """
    from space_time.models import LocalityGeometry

    points = {}
    rows = LocalityGeometry.objects.filter(
        locality_id__in=[locality.pk for locality in localities])
    for row in rows:
        try:
            geometry = shapely_wkb.loads(bytes(row.wkb))
        except Exception:
            continue
        if geometry.is_empty:
            continue
        centre = to_latlon(geometry.centroid)
        points[row.locality_id] = [round(centre.x, 6), round(centre.y, 6)]
    for locality in localities:
        if locality.pk in points:
            continue
        if locality.latitude is None or locality.longitude is None:
            continue
        points[locality.pk] = [locality.longitude, locality.latitude]
    return points


def _centroid(geometry) -> tuple | None:
    """`(lat, lon)` representativo del trazo.

    La línea usa su punto medio: el centroide de una línea curva cae
    fuera de ella y el pin debe estar sobre lo dibujado.
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

# `StatusControl` tiene `name` de llave primaria, así que
# `status_location_id` ya es el nombre interno: comparar contra él evita
# la consulta y no depende del `public_name`, que sí es editable.
APPROXIMATE_STATUS = "Aproximado"


def apply_geolocation(location, geometry_changed: bool = True,
                      write_relations: bool = True) -> list[str]:
    """Escribe en `location` lo derivado y devuelve qué campos tocó.

    No guarda: quien llama decide entre `save()` y `bulk_update`. El M2M
    queda siempre en `location.crossed_municipalities`, aunque
    `write_relations=False` lo deje sin escribir: así el backfill puede
    contarlo antes de respaldar lo anterior.
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
    # El M2M significa «municipios que la geometría atraviesa» (docs
    # `adr-0026`): un punto no atraviesa nada, y copiar ahí su propio
    # municipio solo duplicaba el FK. Se limpia por si quedó algo.
    location.crossed_municipalities = []
    if write_relations and location.pk:
        location.municipalities.clear()
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
    crossed = [municipality.pk
               for municipality, _ in resolution.municipalities]
    location.crossed_municipalities = crossed
    if write_relations and location.pk:
        location.municipalities.set(crossed)
    return filled


def _blocked_fields(location) -> frozenset:
    """Campos que este `Location` no acepta llenar, por su estatus.

    En un punto «Aprobado (Aproximado)» la coordenada señala el rumbo y
    no el sitio: la localidad que resolviera el motor sería una precisión
    falsa. El estado y el municipio sí resisten esa imprecisión.
    """
    if (location.type_location == "point"
            and location.status_location_id == APPROXIMATE_STATUS):
        return frozenset({"locality"})
    return frozenset()


def _fill_empty(location, resolution, municipality_from: str = "") -> list[str]:
    municipality = (
        resolution.single_municipality if municipality_from == "single"
        else resolution.municipality)
    values = {
        "state": getattr(resolution, "state", None),
        "municipality": municipality,
        "locality": resolution.locality,
    }
    blocked = _blocked_fields(location)
    filled = []
    for name in FILLABLE:
        value = values[name]
        if name in blocked:
            continue
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
