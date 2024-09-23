from django.core.management.base import BaseCommand


from event.migrate.accion_colectiva import AccionesColectivasToEventMigrate
from event.migrate.violencia import ViolenciaToEventMigrate
from event.models import Event, EventLocation, Involved


class Command(BaseCommand):
    help = 'Migración de Modelos Legacy a Events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-old-events',
            type=bool,
            help='Delete old events after migration',
        )
        parser.add_argument(
            "--only-violencia",
            type=bool,
            help="Only migrate violencia")
        parser.add_argument(
            "--only-accion-colectiva",
            type=bool,
            help="Only migrate accion colectiva")

    def handle(self, *args, **kwargs):
        delete_old_events = kwargs.get('delete_old_events', False)
        only_violencia = kwargs.get('only_violencia', False)
        only_accion_colectiva = kwargs.get('only_accion_colectiva', False)

        if delete_old_events:
            print("Deleting old events")
            Event.objects.all().delete()
            EventLocation.objects.all().delete()
            Involved.objects.all().delete()

        if only_violencia:
            self.migrate_violencia()
            return

        if only_accion_colectiva:
            self.migrate_accion_colectiva()
            return

        self.migrate_violencia()
        self.migrate_accion_colectiva()

    def migrate_violencia(self):
        print("Starting Violencia migration")
        violencia_migration = ViolenciaToEventMigrate()

        for violencia, error in violencia_migration.errors:
            print(f"Error with violencia {violencia.pk}: {violencia}")
            print(error)
            print()

    def migrate_accion_colectiva(self):
        print("Starting Accion colectiva migration")
        accion_colectiva_migration = AccionesColectivasToEventMigrate()

        for accion_colectiva, error in accion_colectiva_migration.errors:
            print(
                f"Error with accion_colectiva {accion_colectiva.pk}: {accion_colectiva}")
            print(error)
            print()
