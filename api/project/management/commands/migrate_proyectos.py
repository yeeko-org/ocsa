import traceback 
from django.core.management.base import BaseCommand

from project.migrate import ProyectoToProject



class Command(BaseCommand):
    help = 'Migracion de Proyectos a Projects'

    def handle(self, *args, **options):
        migration = ProyectoToProject()

        for proyecto, error in migration.errors:
            print(f"Error with proyecto {proyecto.pk}: {proyecto}")
            print(error)
            traceback.print_exc() 
            print()
