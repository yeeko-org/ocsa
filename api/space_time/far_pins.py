"""Pines lejos de lo capturado: puntos fuera de su municipio o su estado.

Mide con shapely en EPSG:6372 la distancia del pin al polígono del
municipio capturado y al del estado capturado (0 si cae dentro). Sale la
fila cuando el pin está a más de `THRESHOLD_KM` de su municipio o fuera
de su estado: o el pin está mal puesto, o lo capturado no corresponde.

Vive aquí y no en el diagnóstico porque el comando
`flag_locations_for_review` recomputa la misma selección desde los datos
antes de escribir nada.
"""

from dataclasses import dataclass
from functools import lru_cache

from shapely import wkb as shapely_wkb

from space_time.geolocate import point_in_meters, resolve_point
from space_time.models import Location, MunicipalityGeometry, StateGeometry

# Kilómetros: por debajo de esto el desfase cabe en el margen de un
# municipio mal dibujado o un pin puesto «al ojo». Decidido por Ricardo
# el 2026-08-28 (antes eran 10 km).
THRESHOLD_KM = 2.0


@dataclass
class FarPin:
    """Un punto que no cuadra con lo capturado, ya medido y resuelto."""

    location: Location
    to_municipality: float | None
    to_state: float | None
    resolution: object
    threshold: float = THRESHOLD_KM

    @property
    def far_municipality(self) -> bool:
        return (self.to_municipality is not None
                and self.to_municipality > self.threshold)

    @property
    def far_state(self) -> bool:
        return self.to_state is not None and self.to_state > 0


@lru_cache(maxsize=None)
def municipality_polygon(municipality_id: int):
    return _polygon(MunicipalityGeometry, "municipality_id", municipality_id)


@lru_cache(maxsize=None)
def state_polygon(state_id: int):
    return _polygon(StateGeometry, "state_id", state_id)


def _polygon(model, field: str, value: int):
    row = model.objects.filter(**{field: value}).first()
    if row is None:
        return None
    try:
        return shapely_wkb.loads(bytes(row.wkb))
    except Exception:
        return None


def distance_km(point, polygon) -> float | None:
    """Kilómetros del pin al polígono; 0 si cae dentro. `None` si falta."""
    if polygon is None:
        return None
    return round(point.distance(polygon) / 1000.0, 3)


def name_of(entity) -> str:
    return getattr(entity, "name", "") or ""


def universe():
    """Puntos con proyecto y coordenadas: los únicos medibles."""
    return (
        Location.objects
        .filter(type_location="point", project__isnull=False,
                latitude__isnull=False, longitude__isnull=False)
        .select_related("state", "municipality", "project", "status_location")
        .order_by("id"))


def scan(threshold: float = THRESHOLD_KM) -> tuple[list[FarPin], int]:
    """Devuelve los pines lejanos y cuántos puntos se revisaron.

    El umbral solo aplica al municipio: caer fuera del estado capturado
    no admite margen, porque ahí lo capturado y lo calculado se
    contradicen sin ambigüedad.
    """
    found, seen = [], 0
    for location in universe().iterator(chunk_size=500):
        seen += 1
        point = point_in_meters(location.latitude, location.longitude)
        to_municipality = (
            distance_km(point, municipality_polygon(location.municipality_id))
            if location.municipality_id else None)
        to_state = (
            distance_km(point, state_polygon(location.state_id))
            if location.state_id else None)
        far_municipality = (
            to_municipality is not None and to_municipality > threshold)
        far_state = to_state is not None and to_state > 0
        if not far_municipality and not far_state:
            continue
        resolution = resolve_point(
            location.latitude, location.longitude, location.state_id)
        found.append(FarPin(
            location=location, to_municipality=to_municipality,
            to_state=to_state, resolution=resolution, threshold=threshold))
    return found, seen
