"""Trazos que no cuadran con el estado, el municipio o la localidad
capturados.

Proyecta el `geojson` con los mismos helpers del motor
(`space_time/geolocate.py`) y lo compara contra el polígono del municipio
capturado: sale la fila cuando el trazo se aleja de él más que la propia
tolerancia con que se simplificó la capa (`GeometryBase.simplified_m`,
leída de la fila). O el trazo está mal dibujado, o el municipio capturado
no corresponde. La misma comparación, contra el polígono estatal y con
su propia simplificación, es `scan_states`.

Aparte van las dos que no preguntan por contacto sino por recorrido, con
la medida del motor: `scan_base_municipality` —si el trazo **atraviesa**
el municipio capturado— y `scan_in_other_state` —si atraviesa municipios
de un estado ajeno al capturado, aunque no se haya salido del suyo—.

La localidad no se juzga por contacto sino por distancia, con la misma
tolerancia y la misma medida que el pin (`far_pins.scan_localities`):
polígono cuando la localidad es amanzanada, punto del catálogo AGEEML
cuando no lo es. El número vive en `geolocate.LOCALITY_TOLERANCE_M` y de
ahí lo toma también el endpoint que alimenta el aviso en vivo del editor,
para que la marca no diga otra cosa que la pantalla.

Vive aparte por la misma razón que `far_pins.py`: el comando
`flag_locations_for_review` recomputa la selección desde los datos antes
de escribir nada.
"""

from dataclasses import dataclass

from space_time.far_pins import (
    LOCALITY_THRESHOLD_KM, locality_point, locality_polygon,
    municipality_polygon, municipality_simplification_m, state_polygon,
    state_simplification_m)
from space_time.geolocate import feature_to_shape, resolve_geometry
from space_time.models import Location

TRACE_TYPES = ("line", "polygon")


@dataclass
class OffTrace:
    """Un trazo fuera de su municipio, con los que sí atraviesa."""

    location: Location
    crossed: list


@dataclass
class OffState:
    """Un trazo fuera del polígono de su estado, con cuánto se alejó."""

    location: Location
    distance: float


@dataclass
class InOtherState:
    """Un trazo que atraviesa municipios de un estado que no es el suyo."""

    location: Location
    crossed: list


@dataclass
class BaseOffCrossed:
    """Un trazo que no atraviesa su municipio base, con los que sí."""

    location: Location
    crossed: list


@dataclass
class OffLocality:
    """Un trazo lejos de la localidad capturada, con cómo se midió."""

    location: Location
    distance: float
    measured_on: str
    threshold: float = LOCALITY_THRESHOLD_KM


def universe():
    """Líneas y polígonos con trazo y municipio: los únicos medibles."""
    return (
        Location.objects
        .filter(type_location__in=TRACE_TYPES, geojson__isnull=False,
                municipality__isnull=False)
        .select_related("state", "municipality", "project", "status_location")
        .order_by("id"))


def scan() -> tuple[list[OffTrace], int]:
    """Devuelve los trazos fuera de su municipio y cuántos se revisaron.

    Sin umbral editorial, al revés que los municipios atravesados: basta
    con que el trazo roce el municipio capturado para darlo por bueno,
    porque lo que se cuestiona aquí es la captura y no la medida del
    cruce. El único margen es el del dibujo, la simplificación de la
    capa municipal, para que un borde recortado no invente una
    separación que en la cartografía completa no existe.
    """
    found, seen = [], 0
    for location in universe().iterator(chunk_size=500):
        geometry = feature_to_shape(location.geojson)
        if geometry is None or geometry.is_empty:
            continue
        polygon = municipality_polygon(location.municipality_id)
        if polygon is None:
            continue
        seen += 1
        grace = municipality_simplification_m(location.municipality_id)
        if geometry.distance(polygon) <= grace:
            continue
        crossed = [municipality for municipality, _ in resolve_geometry(
            location.geojson, location.state_id).municipalities]
        found.append(OffTrace(location=location, crossed=crossed))
    return found, seen


def state_universe():
    """Líneas y polígonos con trazo y estado: los únicos medibles.

    No se pide municipio: es justo el trazo sin municipio capturado el
    que ninguna otra razón alcanza, y su estado sí se puede contradecir.
    """
    return (
        Location.objects
        .filter(type_location__in=TRACE_TYPES, geojson__isnull=False,
                state__isnull=False)
        .select_related("state", "municipality", "project", "status_location")
        .order_by("id"))


def scan_states() -> tuple[list[OffState], int]:
    """Devuelve los trazos fuera de su estado y cuántos se revisaron.

    Mismo criterio que `scan()` un nivel arriba: la única gracia es la
    simplificación de la capa estatal. No dice a qué estado pertenece de
    verdad: eso lo responde `scan_in_other_state`, que sí recorre los
    municipios atravesados.
    """
    found, seen = [], 0
    for location in state_universe().iterator(chunk_size=500):
        geometry = feature_to_shape(location.geojson)
        if geometry is None or geometry.is_empty:
            continue
        polygon = state_polygon(location.state_id)
        if polygon is None:
            continue
        seen += 1
        distance = geometry.distance(polygon)
        if distance <= state_simplification_m(location.state_id):
            continue
        found.append(OffState(
            location=location, distance=round(distance / 1000.0, 3)))
    return found, seen


def scan_in_other_state() -> tuple[list[InOtherState], int]:
    """Trazos que atraviesan municipios de un estado ajeno al capturado.

    Es la otra mitad de `scan_states`, y la que ve lo que aquella no
    puede: un trazo puede quedar a distancia cero de su estado capturado
    —dentro de él, incluso en su mayor parte— y aun así desbordar la
    frontera. `scan_states` pregunta si el trazo se salió del estado;
    esta, si además entró a otro.

    El cruce se mide con la regla del motor (`resolve_geometry`: 50 m de
    línea o 1 ha de área), así que un roce de frontera por debajo del
    umbral no cuenta: sería el dibujo y no el recorrido.
    """
    found, seen = [], 0
    for location in state_universe().iterator(chunk_size=500):
        geometry = feature_to_shape(location.geojson)
        if geometry is None or geometry.is_empty:
            continue
        seen += 1
        crossed = [municipality for municipality, _ in resolve_geometry(
            location.geojson, location.state_id).municipalities]
        outside = [municipality for municipality in crossed
                   if municipality.state_id != location.state_id]
        if not outside:
            continue
        found.append(InOtherState(location=location, crossed=outside))
    return found, seen


def scan_base_municipality() -> tuple[list[BaseOffCrossed], int]:
    """Trazos cuyo municipio capturado no está entre los atravesados.

    Se solapa con `scan()` pero no lo repite: aquella pregunta si el
    trazo **toca** el municipio capturado, y esta si lo **atraviesa** con
    la medida del motor (`resolve_geometry`: 50 m de línea o 1 ha de
    área). En medio queda el roce —un trazo que entra 49 m al municipio
    capturado y sigue de largo por otro—: `scan()` lo da por bueno y
    esta razón lo saca, que es la incoherencia que ve el editor cuando
    el municipio base capturado no aparece en la lista de atravesados.

    Los atravesados se recalculan y no se leen del M2M para que la
    comparación sea contra lo que el motor diría hoy.
    """
    found, seen = [], 0
    for location in universe().iterator(chunk_size=500):
        geometry = feature_to_shape(location.geojson)
        if geometry is None or geometry.is_empty:
            continue
        seen += 1
        crossed = [municipality for municipality, _ in resolve_geometry(
            location.geojson, location.state_id).municipalities]
        if any(municipality.pk == location.municipality_id
               for municipality in crossed):
            continue
        found.append(BaseOffCrossed(location=location, crossed=crossed))
    return found, seen


def locality_universe():
    """Líneas y polígonos con trazo y localidad: los únicos medibles."""
    return (
        Location.objects
        .filter(type_location__in=TRACE_TYPES, geojson__isnull=False,
                locality__isnull=False)
        .select_related("state", "municipality", "locality", "project",
                        "status_location")
        .order_by("id"))


def scan_localities(
        threshold: float = LOCALITY_THRESHOLD_KM
        ) -> tuple[list[OffLocality], dict]:
    """Trazos lejos de su localidad, y con qué se midió cada revisado.

    La localidad amanzanada se mide contra su polígono; la que solo
    existe como fila del AGEEML, contra su punto de catálogo. Esa
    diferencia importa al leer el umbral: la distancia a un punto incluye
    el radio de la localidad, la distancia al polígono no.
    """
    found = []
    seen = {"seen": 0, "polygon": 0, "point": 0, "unmeasurable": 0}
    for location in locality_universe().iterator(chunk_size=500):
        geometry = feature_to_shape(location.geojson)
        if geometry is None or geometry.is_empty:
            continue
        polygon = locality_polygon(location.locality_id)
        reference = (polygon if polygon is not None
                     else locality_point(location.locality_id))
        measured_on = "polygon" if polygon is not None else "point"
        if reference is None:
            seen["unmeasurable"] += 1
            continue
        seen["seen"] += 1
        seen[measured_on] += 1
        distance = round(geometry.distance(reference) / 1000.0, 3)
        if distance <= threshold:
            continue
        found.append(OffLocality(
            location=location, distance=distance, measured_on=measured_on,
            threshold=threshold))
    return found, seen
