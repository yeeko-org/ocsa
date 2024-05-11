from django.core.management.base import BaseCommand


from event.migrate.accion_colectiva import AccionesColectivasToEventMigrate
from event.migrate.violencia import ViolenciaToEventMigrate
from event.models import Event


class Command(BaseCommand):
    help = 'Migración de Modelos Legacy a Events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-old-events',
            type=bool,
            help='Delete old events after migration',
        )

    def handle(self, *args, **kwargs):
        delete_old_events = kwargs.get('delete_old_events', False)

        if delete_old_events:
            print("Deleting old events")
            Event.objects.all().delete()

        print("Starting Violencia migration")
        violencia_migration = ViolenciaToEventMigrate()

        for violencia, error in violencia_migration.errors:
            print(f"Error with violencia {violencia.pk}: {violencia}")
            print(error)
            print()

        print("Starting Accion colectiva to Event migration")
        accion_colectiva_migration = AccionesColectivasToEventMigrate()

        for accion_colectiva, error in accion_colectiva_migration.errors:
            print(
                f"Error with accion_colectiva {accion_colectiva.pk}: {accion_colectiva}")
            print(error)
            print()
