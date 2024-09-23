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
        ProyectoToUbicacionMigrate()

        set_icons_to_dct()


def set_icons_to_dct():
    from project.models import DeploymentCapitalType
    extractivism_types = [
        ("Extractivismo minero", "landslide"),
        ("Extractivismo agroindustrial, de monocultivo, industria ganadera, explotación forestal y recursos bióticos", "agriculture"),
        ("Hiperurbanización", "apartment"),
        ("Biomercantilización", "yard"),
        ("Extractivismo energético", "wind_power"),
        ("Extractivismo hídrico", "water_drop"),
        ("Megainfraestructura y vías de comunicación", "commute")
    ]
    for name, icon in extractivism_types:
        dct, _ = DeploymentCapitalType.objects.get_or_create(name=name)
        dct.icon = icon
        dct.save()
