import pandas as pd
from django.core.management.base import BaseCommand

from project.models import Project
from space_time.models import Location


class Command(BaseCommand):
    help = 'Lee un archivo Excel, convierte las coordenadas en grados decimales y registra en Project'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='Ruta al archivo Excel con las coordenadas')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            df = pd.read_excel(file_path)

            if not all(col in df.columns for col in ['ID', 'LATITUD', 'LONGITUD']):
                self.stdout.write(self.style.ERROR(
                    'El archivo debe contener las columnas "Latitud" y "Longitud"'))
                return

            for _, row in df.iterrows():
                mp_id = row['ID']
                lat_dms = row['LATITUD']
                lon_dms = row['LONGITUD']

                lat_dd = self.dms_to_dd(lat_dms)
                lon_dd = self.dms_to_dd(lon_dms)

                self.set_project_coordinates(mp_id, lat_dd, lon_dd)

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Error leyendo el archivo: {e}"))

    def dms_to_dd(self, dms):

        try:
            parts = dms.split(" ")
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

    def set_project_coordinates(self, mp_id, lat_dd, lon_dd):
        mp_id = str(mp_id).replace("MP", "").strip()
        if not mp_id.isdigit():
            return
        try:
            project = Project.objects.get(legacy_id_mp=int(mp_id))
        except Project.DoesNotExist:
            return

        Location.objects.filter(projects__project=project).update(
            latitude=lat_dd, longitude=lon_dd)

        project.save()
