"""Ubicaciones cuyo estado capturado no es el del municipio capturado.

No mide nada: compara dos llaves foráneas que el catálogo ya relaciona
—`Municipality.state`— y que en una captura coherente deben coincidir.
Por eso aplica a cualquier `type_location`, con coordenadas o sin ellas.

Vive aparte por la misma razón que `far_pins.py`: el comando
`flag_locations_for_review` recomputa la selección desde los datos antes
de escribir nada.
"""

from dataclasses import dataclass

from space_time.models import Location


@dataclass
class Mismatch:
    """Una ubicación con estado y municipio que no concuerdan."""

    location: Location


def universe():
    """Las que tienen ambos campos: sin los dos no hay contradicción."""
    return (
        Location.objects
        .filter(state__isnull=False, municipality__isnull=False)
        .select_related("state", "municipality__state", "project",
                        "status_location")
        .order_by("id"))


def scan() -> tuple[list[Mismatch], int]:
    """Devuelve las incoherentes y cuántas ubicaciones se revisaron."""
    found, seen = [], 0
    for location in universe().iterator(chunk_size=500):
        seen += 1
        if location.municipality.state_id == location.state_id:
            continue
        found.append(Mismatch(location=location))
    return found, seen
