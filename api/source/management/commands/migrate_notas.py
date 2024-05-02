from django.core.management.base import BaseCommand

from source.migrate import NotaToNote


class Command(BaseCommand):
    help = 'Migracion de Notas a Note'

    def handle(self, *args, **options):
        migration = NotaToNote()

        for nota, error in migration.errors:
            print(f"Error with nota {nota}:")
            print(error)
            print()
