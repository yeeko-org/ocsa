import csv
from django.core.management.base import BaseCommand

from space_time.models import Locality, Municipality


class Command(BaseCommand):
    help = 'Load localidades'

    def handle(self, *args, **options):

        localidades = LoadLocalidades()


class LoadLocalidades:
    localities = []
    municipalities_ids = {}
    batch_size = 10000
    errors = []

    def __init__(self):
        self.load_municipalities()
        self.load_csv("space_time/geo_files/localidades.csv")
        self.bulk_create()

    def load_csv(self, file_path):
        print("Loading localities")
        self.localities = []
        with open(file_path, newline='', encoding='latin1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                municipality_inegi_code = row['CVE_MUN']
                municipality_id = self.municipalities_ids.get(
                    municipality_inegi_code)
                inegi_code = row['CVE_LOC']
                complete_code = f"{municipality_inegi_code}-{inegi_code}"
                name = row['NOM_LOC']
                pob_total = row['POB_TOTAL'] or ""
                population = int(pob_total) if pob_total.isdigit() else None
                latitude = float(row['LAT_DECIMAL'])
                longitude = float(row['LON_DECIMAL'])
                altitude = int(row['ALTITUD'])

                # Crear instancia de Locality
                try:
                    locality = Locality(
                        inegi_code=inegi_code,
                        complete_code=complete_code,
                        name=name,
                        municipality_id=municipality_id,
                        population=population,
                        latitude=latitude,
                        longitude=longitude,
                        altitude=altitude
                    )
                    self.localities.append(locality)
                except Exception as e:
                    self.errors.append(
                        f"Error creating locality {inegi_code}: {e}")

    def load_municipalities(self):
        print("Loading municipalities")

        for municipality in Municipality.objects.all():
            self.municipalities_ids[municipality.inegi_code] = municipality.pk

    def bulk_create(self):
        print("Bulk creating localities")
        for i in range(0, len(self.localities), self.batch_size):
            print(f"Creating localities {i} to {i + self.batch_size}")
            Locality.objects.bulk_create(
                self.localities[i:i + self.batch_size])
