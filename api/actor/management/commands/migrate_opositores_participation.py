from django.core.management.base import BaseCommand

from actor.migrate.opositores import OpositorAddParticipantMigration


class Command(BaseCommand):
    help = 'Migración de las menciones de participación de los opositores'

    def handle(self, *args, **kwargs):

        print("Starting OpositorAddParticipantMigration")
        opositor_participation_migration = OpositorAddParticipantMigration()

        for opositor, error in opositor_participation_migration.errors:
            print(f"Error with status {opositor.pk}: {opositor}")
            print(error)
            print()
