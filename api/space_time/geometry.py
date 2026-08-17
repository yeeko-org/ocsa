"""Contrato de `Location.geojson` y utilidades de geometría.

`Location.geojson` es `null` o un único Feature de GeoJSON (RFC 7946)
cuyo `geometry.type` concuerda con `type_location`: `line` admite
LineString o MultiLineString, `polygon` admite Polygon o MultiPolygon, y
`point` no guarda geojson (el punto vive en `latitude`/`longitude`).
Las coordenadas son 2D, sin miembro `crs` y sin partes vacías o
degeneradas.

Módulo de Python puro: no depende de GEOS ni de librerías externas.
"""

from __future__ import annotations

from typing import Any, Iterator

from django.db.models import Q

Position = list[float]

SIMPLE_TYPES = {
    "point": "Point",
    "line": "LineString",
    "polygon": "Polygon",
}
MULTI_TYPES = {
    "point": "MultiPoint",
    "line": "MultiLineString",
    "polygon": "MultiPolygon",
}
TYPE_LOCATION_BY_GEOMETRY = {
    "Point": "point",
    "MultiPoint": "point",
    "LineString": "line",
    "MultiLineString": "line",
    "Polygon": "polygon",
    "MultiPolygon": "polygon",
}
SIMPLE_BY_MULTI = {
    "MultiPoint": "Point",
    "MultiLineString": "LineString",
    "MultiPolygon": "Polygon",
}

# Mínimo de posiciones para que la parte tenga extensión real; un anillo
# se mide ya cerrado, por eso pide una más que la línea.
MIN_POSITIONS = {"Point": 1, "LineString": 2, "Ring": 4}


def geometry_type_for(type_location: str) -> tuple[str, str]:
    """Tipos (simple, múltiple) que admite un tipo de ubicación."""
    try:
        return SIMPLE_TYPES[type_location], MULTI_TYPES[type_location]
    except KeyError:
        raise ValueError(
            f"Tipo de ubicación desconocido: {type_location!r}.") from None


def type_location_for(geometry_type: str) -> str | None:
    """Tipo de ubicación que corresponde a un `geometry.type`."""
    return TYPE_LOCATION_BY_GEOMETRY.get(geometry_type)


def infer_type_location(value: Any) -> str | None:
    """Deduce el tipo de ubicación a partir del contenido del geojson."""
    try:
        geometries, _, _ = _unwrap(value)
    except ValueError:
        return None
    for geometry in geometries:
        found = TYPE_LOCATION_BY_GEOMETRY.get(geometry.get("type"))
        if found:
            return found
    return None


def has_geometry(location: Any) -> bool:
    """Fuente única de verdad de «esta ubicación está ubicada».

    Par completo de coordenadas (una sola no ubica) o geojson presente.
    """
    latitude = getattr(location, "latitude", None)
    longitude = getattr(location, "longitude", None)
    if latitude is not None and longitude is not None:
        return True
    return bool(getattr(location, "geojson", None))


def has_geometry_q(prefix: str = "") -> Q:
    """`has_geometry` en versión ORM, para filtrar en la base.

    `prefix` permite atravesar una relación (p. ej. `"locations__"`).
    Un geojson cuenta solo si es un objeto GeoJSON: la clave `type`
    descarta de paso el `null` de JSON y el objeto vacío.
    """
    coordinates = (
        Q(**{f"{prefix}latitude__isnull": False})
        & Q(**{f"{prefix}longitude__isnull": False}))
    return coordinates | Q(**{f"{prefix}geojson__type__isnull": False})


def no_geometry_q(prefix: str = "") -> Q:
    """Negación exacta de `has_geometry_q`, en forma positiva.

    Se escribe aparte porque negar una Q que atraviesa una relación
    múltiple cambia su semántica (pasa a NOT EXISTS sobre el conjunto).
    """
    missing_coordinates = (
        Q(**{f"{prefix}latitude__isnull": True})
        | Q(**{f"{prefix}longitude__isnull": True}))
    return missing_coordinates & Q(**{f"{prefix}geojson__type__isnull": True})


def normalize_geojson(value: Any, type_location: str) -> dict | None:
    """Normaliza cualquier entrada razonable al Feature único del contrato.

    Envuelve geometrías sueltas, fusiona una FeatureCollection homogénea
    en una geometría Multi* y descarta partes vacías o degeneradas.
    Devuelve `None` cuando no queda geometría. Lanza `ValueError` (en
    español, apto para mostrarse) si la entrada es inconsistente.
    """
    simple_type, multi_type = geometry_type_for(type_location)
    if not value:
        return None
    geometries, properties, identifier = _unwrap(value)
    parts: list[tuple[str, Any]] = []
    for geometry in geometries:
        for kind, coordinates in _simple_parts(geometry):
            cleaned = _clean_part(kind, coordinates)
            if cleaned is not None:
                parts.append((kind, cleaned))
    if not parts:
        return None
    kinds = {kind for kind, _ in parts}
    if len(kinds) > 1:
        raise ValueError(
            "El geojson mezcla geometrías de distinto tipo (%s); una "
            "ubicación solo admite un tipo." % ", ".join(sorted(kinds)))
    kind = kinds.pop()
    if kind != simple_type:
        raise ValueError(
            f"La geometría es de tipo {kind} y la ubicación es de tipo "
            f"«{type_location}», que espera {simple_type} o {multi_type}.")
    if kind == "Point" and len(parts) > 1:
        raise ValueError(
            "Una ubicación de tipo punto no admite varios puntos.")
    if len(parts) == 1:
        geometry = {"type": kind, "coordinates": parts[0][1]}
    else:
        geometry = {
            "type": multi_type,
            "coordinates": [coordinates for _, coordinates in parts],
        }
    feature: dict[str, Any] = {"type": "Feature"}
    if identifier is not None:
        feature["id"] = identifier
    feature["properties"] = properties if isinstance(properties, dict) else {}
    feature["geometry"] = geometry
    return feature


def normalize_location_geometry(
        geojson: Any, type_location: str,
        latitude: float | None = None,
        longitude: float | None = None,
) -> tuple[dict | None, float | None, float | None]:
    """Aplica el contrato al trío `(geojson, latitude, longitude)`.

    El contrato es de los tres campos juntos: un Point dibujado sobre una
    ubicación de tipo punto se guarda como par de coordenadas y deja el
    geojson nulo.
    """
    feature = normalize_geojson(geojson, type_location)
    if type_location == "point":
        if feature is not None:
            longitude, latitude = feature["geometry"]["coordinates"][:2]
        return None, latitude, longitude
    return feature, latitude, longitude


def round_coordinates(geometry: dict, ndigits: int = 5) -> dict:
    """Redondea las coordenadas de una geometría a cualquier profundidad."""
    rounded = dict(geometry)
    if "coordinates" in rounded:
        rounded["coordinates"] = _round_nested(
            rounded["coordinates"], ndigits)
    if "geometries" in rounded:
        rounded["geometries"] = [
            round_coordinates(sub, ndigits)
            for sub in rounded["geometries"] or []]
    return rounded


def iter_geometries(value: Any) -> Iterator[dict]:
    """Recorre las geometrías de un Feature, FeatureCollection o geometría."""
    try:
        geometries, _, _ = _unwrap(value)
    except ValueError:
        return
    yield from geometries


def bounds(value: Any) -> tuple[float, float, float, float] | None:
    """Caja envolvente `(min_lon, min_lat, max_lon, max_lat)` del geojson."""
    positions = [
        position
        for geometry in iter_geometries(value)
        for _, coordinates in _simple_parts(geometry)
        for position in _iter_positions(coordinates)
    ]
    if not positions:
        return None
    lons = [position[0] for position in positions]
    lats = [position[1] for position in positions]
    return min(lons), min(lats), max(lons), max(lats)


def display_geometry(
        geojson: Any = None, type_location: str | None = None,
        latitude: float | None = None, longitude: float | None = None,
        ndigits: int = 5,
) -> dict | None:
    """Geometría lista para emitir en el mapa público.

    Tolerante con lo que hoy hay en la base: si `type_location` contradice
    al geojson manda el contenido real de la geometría. Devuelve `None`
    cuando no hay nada que pintar y lanza `ValueError` solo si el geojson
    es irreparable (mezcla de tipos).
    """
    point = _point_geometry(latitude, longitude, ndigits)
    if type_location == "point" and point is not None:
        return point
    inferred = infer_type_location(geojson)
    if inferred is None:
        return point
    feature = normalize_geojson(geojson, inferred)
    if feature is None:
        return point
    return round_coordinates(feature["geometry"], ndigits)


def to_feature(location: Any, properties: dict | None = None,
               ndigits: int = 5) -> dict | None:
    """Feature de salida de una `Location` (o de un dict con sus campos)."""
    read = location.get if isinstance(location, dict) else (
        lambda key: getattr(location, key, None))
    geometry = display_geometry(
        read("geojson"), read("type_location"),
        read("latitude"), read("longitude"), ndigits)
    if geometry is None:
        return None
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties or {},
    }


def _point_geometry(latitude: float | None, longitude: float | None,
                    ndigits: int) -> dict | None:
    if latitude is None or longitude is None:
        return None
    return {
        "type": "Point",
        "coordinates": [round(longitude, ndigits), round(latitude, ndigits)],
    }


def _unwrap(value: Any) -> tuple[list[dict], dict | None, Any]:
    """Devuelve `(geometrías, properties, id)` de cualquier envoltorio."""
    if not isinstance(value, dict):
        raise ValueError(
            "El geojson debe ser un objeto GeoJSON, no "
            f"{type(value).__name__}.")
    kind = value.get("type")
    if kind == "FeatureCollection":
        features = value.get("features") or []
        geometries: list[dict] = []
        properties: dict | None = None
        identifier = None
        for feature in features:
            sub_geometries, sub_properties, sub_id = _unwrap(feature)
            geometries.extend(sub_geometries)
            if properties is None:
                properties, identifier = sub_properties, sub_id
        # El id de mapbox-draw identifica un dibujo, no la fusión de varios.
        if len(features) != 1:
            identifier = None
        return geometries, properties, identifier
    if kind == "Feature":
        geometry = value.get("geometry")
        geometries = [] if geometry is None else _unwrap(geometry)[0]
        return geometries, value.get("properties"), value.get("id")
    if kind == "GeometryCollection":
        geometries = []
        for sub in value.get("geometries") or []:
            geometries.extend(_unwrap(sub)[0])
        return geometries, None, None
    if kind in TYPE_LOCATION_BY_GEOMETRY:
        return [value], None, None
    raise ValueError(f"Tipo de geojson no reconocido: {kind!r}.")


def _simple_parts(geometry: dict) -> list[tuple[str, Any]]:
    """Descompone una geometría en partes simples `(tipo, coordenadas)`."""
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    simple = SIMPLE_BY_MULTI.get(kind)
    if simple:
        return [(simple, part) for part in coordinates]
    if kind in SIMPLE_TYPES.values():
        return [(kind, coordinates)]
    return []


def _clean_part(kind: str, coordinates: Any) -> Any | None:
    if kind == "Point":
        return _clean_position(coordinates)
    if kind == "LineString":
        return _clean_line(coordinates, MIN_POSITIONS["LineString"])
    if kind == "Polygon":
        return _clean_polygon(coordinates)
    return None


def _clean_position(position: Any) -> Position | None:
    if not isinstance(position, (list, tuple)) or len(position) < 2:
        return None
    try:
        return [float(position[0]), float(position[1])]
    except (TypeError, ValueError):
        return None


def _clean_line(coordinates: Any, minimum: int) -> list[Position] | None:
    if not isinstance(coordinates, (list, tuple)):
        return None
    positions = [
        cleaned for position in coordinates
        if (cleaned := _clean_position(position)) is not None]
    return positions if len(positions) >= minimum else None


def _clean_ring(coordinates: Any) -> list[Position] | None:
    positions = _clean_line(coordinates, 1)
    if positions is None:
        return None
    if positions[0] != positions[-1]:
        positions.append(list(positions[0]))
    if len(positions) < MIN_POSITIONS["Ring"]:
        return None
    return positions


def _clean_polygon(rings: Any) -> list[list[Position]] | None:
    if not isinstance(rings, (list, tuple)) or not rings:
        return None
    cleaned = [ring for raw in rings if (ring := _clean_ring(raw)) is not None]
    if not cleaned:
        return None
    # RFC 7946: anillo exterior antihorario, agujeros horarios.
    exterior, holes = cleaned[0], cleaned[1:]
    if _signed_area(exterior) < 0:
        exterior = exterior[::-1]
    holes = [hole[::-1] if _signed_area(hole) > 0 else hole for hole in holes]
    return [exterior, *holes]


def _signed_area(ring: list[Position]) -> float:
    """Área con signo (fórmula del zapatero): positiva si es antihoraria."""
    total = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        total += x1 * y2 - x2 * y1
    return total / 2


def _round_nested(value: Any, ndigits: int) -> Any:
    if isinstance(value, (list, tuple)):
        return [_round_nested(item, ndigits) for item in value]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(value, ndigits)
    return value


def _iter_positions(coordinates: Any) -> Iterator[Position]:
    if not isinstance(coordinates, (list, tuple)) or not coordinates:
        return
    if isinstance(coordinates[0], (int, float)):
        position = _clean_position(coordinates)
        if position is not None:
            yield position
        return
    for item in coordinates:
        yield from _iter_positions(item)
