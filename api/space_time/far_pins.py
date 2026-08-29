"""Pines lejos de lo capturado: puntos fuera de su municipio, su estado
o su localidad.

Mide con shapely en EPSG:6372 la distancia del pin al polígono del
municipio capturado y al del estado capturado (0 si cae dentro). Sale la
fila cuando el pin está a más de `THRESHOLD_KM` de su municipio o fuera
de su estado: o el pin está mal puesto, o lo capturado no corresponde.

Fuera del estado se juzga sin umbral editorial, pero no sin margen: los
polígonos del INEGI se guardan simplificados, y un pin sobre el borde
puede caer unos metros del lado de afuera por el dibujo y no por la
captura. El margen es la tolerancia con que se simplificó la capa
(`GeometryBase.simplified_m`), leída de la fila y no fijada aquí.

La distancia a la localidad capturada se mide aparte (`scan_localities`)
porque su universo es otro —los puntos con localidad, tengan o no
municipio— y porque su umbral se decide por separado.

Vive aquí y no en el diagnóstico porque el comando
`flag_locations_for_review` recomputa la misma selección desde los datos
antes de escribir nada.
"""

from dataclasses import dataclass
from functools import lru_cache

from shapely import wkb as shapely_wkb

from space_time.geolocate import (
    APPROXIMATE_STATUS, LOCALITY_TOLERANCE_M, point_in_meters, resolve_point)
from space_time.models import (
    Locality, LocalityGeometry, Location, MunicipalityGeometry, StateGeometry)

# Kilómetros: cualquier desfase que ya no quepa en el ruido cartográfico.
# Son 25 veces la simplificación de la capa municipal (20 m), así que lo
# que sale es captura y no dibujo. Decidido por Ricardo el 2026-08-29
# (antes 2 km, y antes 10 km).
THRESHOLD_KM = 0.5

# La localidad admite más margen que el municipio y no lo hereda: el
# número es el mismo que el editor aplica al trazo, y vive una sola vez
# en `geolocate.LOCALITY_TOLERANCE_M`.
LOCALITY_THRESHOLD_KM = LOCALITY_TOLERANCE_M / 1000.0


@dataclass
class FarPin:
    """Un punto que no cuadra con lo capturado, ya medido y resuelto."""

    location: Location
    to_municipality: float | None
    to_state: float | None
    resolution: object
    threshold: float = THRESHOLD_KM
    # Kilómetros de gracia contra el estado: la simplificación de la capa.
    state_grace: float = 0.0

    @property
    def far_municipality(self) -> bool:
        return (self.to_municipality is not None
                and self.to_municipality > self.threshold)

    @property
    def far_state(self) -> bool:
        return (self.to_state is not None
                and self.to_state > self.state_grace)


@dataclass
class FarLocalityPin:
    """Un punto lejos de la localidad capturada, con cómo se midió."""

    location: Location
    distance: float
    measured_on: str
    threshold: float = LOCALITY_THRESHOLD_KM


@lru_cache(maxsize=None)
def municipality_polygon(municipality_id: int):
    return _polygon(MunicipalityGeometry, "municipality_id", municipality_id)


@lru_cache(maxsize=None)
def state_polygon(state_id: int):
    return _polygon(StateGeometry, "state_id", state_id)


@lru_cache(maxsize=None)
def locality_polygon(locality_id: int):
    return _polygon(LocalityGeometry, "locality_id", locality_id)


@lru_cache(maxsize=None)
def locality_point(locality_id: int):
    """Punto del catálogo AGEEML, para las localidades sin polígono."""
    row = (Locality.objects.filter(pk=locality_id)
           .only("latitude", "longitude").first())
    if row is None or row.latitude is None or row.longitude is None:
        return None
    return point_in_meters(row.latitude, row.longitude)


@lru_cache(maxsize=None)
def state_simplification_m(state_id: int) -> float:
    return _simplification_m(StateGeometry, "state_id", state_id)


@lru_cache(maxsize=None)
def municipality_simplification_m(municipality_id: int) -> float:
    return _simplification_m(
        MunicipalityGeometry, "municipality_id", municipality_id)


def _polygon(model, field: str, value: int):
    row = model.objects.filter(**{field: value}).first()
    if row is None:
        return None
    try:
        return shapely_wkb.loads(bytes(row.wkb))
    except Exception:
        return None


def _simplification_m(model, field: str, value: int) -> float:
    """Metros con que se simplificó ese polígono, 0 si no hay fila.

    Es el margen de las comprobaciones sin umbral editorial: por debajo
    de la propia tolerancia del dibujo no hay nada que reportarle a un
    editor.
    """
    row = (model.objects.filter(**{field: value})
           .only("simplified_m").first())
    if row is None or row.simplified_m is None:
        return 0.0
    return float(row.simplified_m)


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

    El umbral editorial solo aplica al municipio: caer fuera del estado
    capturado no admite margen de captura, porque ahí lo capturado y lo
    calculado se contradicen sin ambigüedad. Sí admite el margen del
    dibujo, la simplificación de la capa estatal.
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
        grace = (state_simplification_m(location.state_id) / 1000.0
                 if location.state_id else 0.0)
        far_municipality = (
            to_municipality is not None and to_municipality > threshold)
        far_state = to_state is not None and to_state > grace
        if not far_municipality and not far_state:
            continue
        resolution = resolve_point(
            location.latitude, location.longitude, location.state_id)
        found.append(FarPin(
            location=location, to_municipality=to_municipality,
            to_state=to_state, resolution=resolution, threshold=threshold,
            state_grace=grace))
    return found, seen


def locality_universe():
    """Puntos con coordenadas y localidad capturada: los medibles.

    No se pide proyecto, al revés que `universe()`: la incoherencia es
    entre la coordenada y el catálogo, y existe igual sin ficha detrás.

    Los puntos «Aprobado (Aproximado)» quedan fuera, y solo de aquí: su
    coordenada señala el rumbo y no el sitio, así que medirle kilómetros
    a la localidad no dice nada —el motor tampoco se la llena—. Contra
    el municipio y contra el estado sí se miden: esas dos resisten la
    imprecisión.
    """
    return (
        Location.objects
        .filter(type_location="point", locality__isnull=False,
                latitude__isnull=False, longitude__isnull=False)
        .exclude(status_location_id=APPROXIMATE_STATUS)
        .select_related("state", "municipality", "locality", "project",
                        "status_location")
        .order_by("id"))


def scan_localities(
        threshold: float = LOCALITY_THRESHOLD_KM
        ) -> tuple[list[FarLocalityPin], dict]:
    """Pines lejos de su localidad, y con qué se midió cada revisada.

    La localidad amanzanada se mide contra su polígono; la que solo
    existe como fila del AGEEML, contra su punto de catálogo. Esa
    diferencia importa al elegir umbral: la distancia a un punto incluye
    el radio de la localidad, la distancia al polígono no.
    """
    found = []
    seen = {"seen": 0, "polygon": 0, "point": 0, "unmeasurable": 0}
    for location in locality_universe().iterator(chunk_size=500):
        point = point_in_meters(location.latitude, location.longitude)
        polygon = locality_polygon(location.locality_id)
        if polygon is not None:
            distance, measured_on = distance_km(point, polygon), "polygon"
        else:
            reference = locality_point(location.locality_id)
            distance = (None if reference is None
                        else round(point.distance(reference) / 1000.0, 3))
            measured_on = "point"
        if distance is None:
            seen["unmeasurable"] += 1
            continue
        seen["seen"] += 1
        seen[measured_on] += 1
        if distance <= threshold:
            continue
        found.append(FarLocalityPin(
            location=location, distance=distance, measured_on=measured_on,
            threshold=threshold))
    return found, seen
