import traceback
from django.core.management.base import BaseCommand

from actor.migrate.capital import CapitalToActorMigration


class Command(BaseCommand):
    help = 'Migracion de Modelos Legacy a Actors'

    def handle(self, *args, **options):

        print("Starting Capital to Actor migration")
        capital_migration = CapitalToActorMigration()

        for capital, error in capital_migration.errors:
            print(f"Error with capital {capital.pk}: {capital}")
            print(error)
            traceback.print_exc()
            print()
