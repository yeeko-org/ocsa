import json
from typing import Dict, Tuple
from actor.migrate.common import text_normalizer
from ocsa_legacy.models import Ubicacion
from space_time.models import Locality, Location, Municipality, State


class UbicacionesToLocations:
    states: Dict[str, int] = {}
    errors = []

    def __init__(self):
        for ubicacion in Ubicacion.objects.all():
            try:
                self.migrate_ubicacion(ubicacion)
            except Exception as e:
                self.errors.append([ubicacion, e])

    def load_states(self):
        for state in State.objects.all():
            self.states[text_normalizer(state.name.lower())] = state.pk

            for alt_name in state.alternative_names:
                self.states[text_normalizer(alt_name.lower())] = state.pk

    def get_state_id(self, state_name: str | None) -> int | None:
        if not state_name:
            return None
        return self.states.get(text_normalizer(state_name.lower()), None)

    def get_municipality(
        self, state_id: int | None,
        municipality_name: str | None
    ) -> Tuple[Municipality | None, int]:

        if not municipality_name:
            return None, 0

        municipality_query = Municipality.objects.filter(
            state_id=state_id, name__iexact=municipality_name)
        municipality_count = municipality_query.count()

        if not municipality_count:
            return None, municipality_count

        return municipality_query.first(), municipality_count

    def get_locality(
        self, municipality: Municipality | None,
        locality_name: str | None
    ) -> Tuple[Locality | None, int]:

        if not locality_name or not municipality:
            return None, 0

        locality_query = Locality.objects.filter(
            municipality=municipality, name__iexact=locality_name)
        locality_count = locality_query.count()

        if not locality_count:
            return None, locality_count

        return locality_query.first(), locality_count

    def migrate_ubicacion(self, ubicacion: Ubicacion):
        details = ""

        if ubicacion.tipo_ubicacion != "punto":
            details += f"Tipo de ubicación: {ubicacion.tipo_ubicacion}.\n\r"

        state_id = self.get_state_id(ubicacion.estado)
        if not state_id:
            details += f"Estado no encontrado: {ubicacion.estado}.\n\r"

        municipality, municipality_count = self.get_municipality(
            state_id, ubicacion.municipio)
        if not municipality:
            details += f"Municipio no encontrado: {ubicacion.municipio}.\n\r"
        if municipality_count > 1:
            details += (
                f"Se encontraron {municipality_count} municipios con el mismo "
                f"nombre{ubicacion.municipio}.\n\r")

        locality, locality_count = self.get_locality(
            municipality, ubicacion.localidad)
        if not locality and ubicacion.localidad:
            details += f"Localidad no encontrada: {ubicacion.localidad}.\n\r"
        if locality_count > 1:
            details += (
                f"Se encontraron {locality_count} localidades con el mismo "
                f"nombre{ubicacion.localidad}.\n\r")

        details = (ubicacion.especificaciones or "") + "\n\r" + details
        details = details.strip()

        geojson = None
        try:
            geojson = json.loads(ubicacion.geom) if ubicacion.geom else None
        except json.JSONDecodeError:
            details += (
                "Error al parsear el geojson. "
                "El campo se guardará como nulo.\n\r")

        Location.objects.create(
            state_id=state_id,
            municipality=municipality,
            locality=locality,
            details=details,
            latitude=ubicacion.latitud,
            longitude=ubicacion.longitud,
            geojson=geojson,
            ubicacion_id_ref=ubicacion.pk
        )
