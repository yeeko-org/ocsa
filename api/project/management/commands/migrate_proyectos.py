import traceback
from django.core.management.base import BaseCommand

from project.migrate import ProyectoToProject, ProyectoToUbicacionMigrate
from space_time.migrate import EstatusProyectoToStatusProject


class Command(BaseCommand):
    help = 'Migracion de Proyectos a Projects'

    def handle(self, *args, **options):

        print("Starting Proyecto to Project migration")
        migration = ProyectoToProject()

        for proyecto, error in migration.errors:
            print(f"Error with proyecto {proyecto.pk}: {proyecto}")
            print(error)
            traceback.print_exc()
            print()

        print("Starting EstatusProyecto to StatusProject migration")
        status_migration = EstatusProyectoToStatusProject()

        for estatus, error in status_migration.errors:
            print(f"Error with estatus {estatus.pk}: {estatus}")
            print(error)
            traceback.print_exc()
            print()

        print("Starting ProyectoToUbicacion migration")
        ubicacion_migration = ProyectoToUbicacionMigrate()
