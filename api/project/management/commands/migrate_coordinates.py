from typing import Dict, Tuple

import pandas as pd
from django.core.management.base import BaseCommand

from actor.migrate.common import text_normalizer
from project.models import Project
from space_time.models import Locality, Location, Municipality, State


class Command(BaseCommand):
    states: Dict[str, int] = {}
    errors = []
    help = 'Lee un archivo Excel, convierte las coordenadas en grados decimales y registra en Project'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='Ruta al archivo Excel con las coordenadas')

    def handle(self, *args, **kwargs):
        self.states = {}
        self.errors = []
        self.load_states()
        file_path = kwargs['file_path']

        try:
            df = pd.read_excel(
                file_path, dtype="string", na_filter=False,
                keep_default_na=False)

            expected_columns = [
                "ID",
                "Estado",
                "Municipio",
                "Localidad",
                "Latitud",
                "Longitud",
            ]

            if not all(col in df.columns for col in expected_columns):
                self.stdout.write(self.style.ERROR(
                    'El archivo debe contener las columnas "Latitud" y "Longitud"'))
                return

            for index, row in df.iterrows():
                mp_id = row['ID']
                lat_dms = row['Latitud']
                lon_dms = row['Longitud']
                state_name = row.get('Estado', None)
                municipality_name = row.get('Municipio', None)
                locality_name = row.get('Localidad', None)

                state_name = None if state_name == "SD" else state_name
                municipality_name = None if municipality_name == "SD" else municipality_name
                locality_name = None if locality_name == "SD" else locality_name
                try:
                    lat_dd = self.dms_to_dd(lat_dms)
                    lon_dd = self.dms_to_dd(lon_dms)
                except ValueError as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error convirtiendo coordenadas {index}: {e}"))
                    continue

                self.set_project_coordinates(
                    mp_id, lat_dd, lon_dd, state_name, municipality_name,
                    locality_name)

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Error leyendo el archivo: {e}"))

        self.set_min_status()

    def set_min_status(self):
        projects = Project.objects.all().prefetch_related('locations')
        custom_order = [
            'empty', 'need_fix', 'could_enhance', 'need_consensus',
            'initial', 'initial_v1', 'filled', 'migrated_v1',
            'Aproximado', 'finished']
        for project in projects:
            status_locations = project.locations.values_list(
                'status_location_id', flat=True)
            if status_locations:
                custom_min = min(
                    [custom_order.index(st) for st in status_locations])
                status_location = custom_order[custom_min]
                project.status_location_id = status_location
            if not project.status_location_id:
                project.status_location_id = 'empty'
            project.save()

    def dms_to_dd(self, dms: str) -> float:

        dms = dms.replace("°", "° ").replace("'", "' ")\
            .replace('"', '" ')

        try:
            parts = dms.split(" ")
            parts = [part for part in parts if part]
            degrees = float(parts[0][:-1])
            minutes = float(parts[1][:-1])
            seconds = float(parts[2][:-1])
            direction = parts[3]

            dd = degrees + (minutes / 60) + (seconds / 3600)

            if direction in ['S', 'W']:
                dd *= -1

            return dd
        except Exception as e:
            raise ValueError(
                f"Formato de coordenadas DMS no válido: {dms}. Error: {e}")

    def set_project_coordinates(
            self, mp_id, lat_dd, lon_dd, state_name, municipality_name,
            locality_name):
        mp_id = str(mp_id).replace("MP", "").strip()
        if not mp_id.isdigit():
            return
        try:
            project = Project.objects.get(proyecto_id_ref=int(mp_id))
        except Project.DoesNotExist:
            return

        Location.objects\
            .filter(project=project, geojson__isnull=True)\
            .delete()

        comments = []

        type_location = "point"

        state_id = self.get_state_id(state_name)
        if not state_id and state_name:
            comments.append(f"Estado no encontrado: {state_name}")

        municipality, municipality_count = self.get_municipality(
            state_id, municipality_name)
        if not municipality and municipality_name:
            comments.append(f"Municipio no encontrado: {municipality_name}")
        if municipality_count > 1:
            comments.append(
                f"Se encontraron {municipality_count} municipios con el mismo "
                f"nombre{municipality_name}")

        locality, locality_count = self.get_locality(
            municipality, locality_name)
        if not locality and locality_name:
            comments.append(f"Localidad no encontrada: {locality_name}")
        if locality_count > 1:
            comments.append(
                f"Se encontraron {locality_count} localidades con el mismo "
                f"nombre{locality_name}")

        final_comments = None
        if comments:
            final_comments = "; ".join(comments)
            final_comments = f"YEEKO: {final_comments}"

        location = Location.objects.create(
            project=project,
            latitude=lat_dd,
            longitude=lon_dd,
            status_location_id="finished",

            state_id=state_id,
            municipality=municipality,
            locality=locality,
            comments=final_comments,
            type_location=type_location
        )

        project.status_location_id = "migrated_v1"  # type: ignore
        project.save()
        self.stdout.write(self.style.SUCCESS(
            f"Coordenadas registradas para el proyecto {project} en {location}"))

    def load_states(self):
        for state in State.objects.all():
            self.states[text_normalizer(
                (state.short_name or state.name).lower())] = state.pk

            for alt_name in state.alternative_names:
                self.states[text_normalizer(alt_name.lower())] = state.pk

    def get_state_id(self, state_name: str | None) -> int | None:
        if not state_name:
            return None
        if not isinstance(state_name, str):
            self.stdout.write(self.style.ERROR(
                f"Estado no es string: {state_name}"))
            return None
        return self.states.get(text_normalizer(state_name.lower()), None)

    def get_municipality(
        self, state_id: int | None,
        municipality_name: str | None
    ) -> Tuple[Municipality | None, int]:

        if not municipality_name:
            return None, 0

        if not isinstance(municipality_name, str):
            self.stdout.write(self.style.ERROR(
                f"Municipio no es string: {municipality_name}"))
            return None, 0

        std_name = text_normalizer(municipality_name)

        municipality_query = Municipality.objects.filter(
            state_id=state_id, std_name=std_name)
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

        if not isinstance(locality_name, str):
            self.stdout.write(self.style.ERROR(
                f"Localidad no es string: {locality_name}"))
            return None, 0

        locality_query = Locality.objects.filter(
            municipality=municipality, name__iexact=locality_name)
        locality_count = locality_query.count()

        if not locality_count:
            return None, locality_count

        return locality_query.first(), locality_count


def dms_to_dd(dms: str) -> float:

    dms = dms.replace("°", "° ").replace("'", "' ")\
        .replace('"', '" ')

    try:
        parts = dms.split(" ")
        parts = [part for part in parts if part]
        degrees = float(parts[0][:-1])
        minutes = float(parts[1][:-1])
        seconds = float(parts[2][:-1])
        direction = parts[3]

        dd = degrees + (minutes / 60) + (seconds / 3600)

        if direction in ['S', 'W']:
            dd *= -1

        return dd
    except Exception as e:
        raise ValueError(
            f"Formato de coordenadas DMS no válido: {dms}. Error: {e}")
