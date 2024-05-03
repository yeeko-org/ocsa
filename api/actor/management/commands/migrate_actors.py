import traceback
from django.core.management.base import BaseCommand

from actor.migrate.status_project import MigrateStatusProject
from actor.migrate.capital import CapitalToActorMigration


class Command(BaseCommand):
    help = 'Migración de Modelos Legacy a Actors'

    def handle(self, *args, **options):

        print("Starting StatusProject migration")
        status_project_migration = MigrateStatusProject()

        for status, error in status_project_migration.errors:
            print(f"Error with status {status.pk}: {status}")
            print(error)
            traceback.print_exc()
            print()

        print("Starting Capital to Actor migration")
        capital_migration = CapitalToActorMigration()

        for capital, error in capital_migration.errors:
            print(f"Error with capital {capital.pk}: {capital}")
            print(error)
            traceback.print_exc()
            print()

