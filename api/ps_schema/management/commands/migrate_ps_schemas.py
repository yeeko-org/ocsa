from django.core.management.base import BaseCommand
from ps_schema.initial_data import InitCollections


class Command(BaseCommand):
    help = 'Carga de datos iniciales de ps_schema'

    def handle(self, *args, **options):
        print('Cargando datos iniciales de ps_schema')
        InitCollections()
        print('Datos iniciales de ps_schema cargados')
