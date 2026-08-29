"""Trazos que no tocan el municipio o la localidad capturados.

Proyecta el `geojson` con los mismos helpers del motor
(`space_time/geolocate.py`) y lo compara contra el polígono del municipio
capturado: sale la fila cuando la intersección es vacía. O el trazo está
mal dibujado, o el municipio capturado no corresponde.

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
    municipality_polygon)
from space_time.geolocate import feature_to_shape, resolve_geometry
from space_time.models import Location

TRACE_TYPES = ("line", "polygon")


@dataclass
class OffTrace:
    """Un trazo fuera de su municipio, con los que sí atraviesa."""

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

    Sin umbral, al revés que los municipios atravesados: basta con que el
    trazo roce el municipio capturado para darlo por bueno, porque lo que
    se cuestiona aquí es la captura y no la medida del cruce.
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
        if geometry.intersects(polygon):
            continue
        crossed = [municipality for municipality, _ in resolve_geometry(
            location.geojson, location.state_id).municipalities]
        found.append(OffTrace(location=location, crossed=crossed))
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
