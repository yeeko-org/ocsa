from django.core.management.base import BaseCommand

from source.migrate import NotaToNote
from source.models import Note


class Command(BaseCommand):
    help = 'Migracion de Notas a Note'

    def handle(self, *args, **options):
        migration = NotaToNote()

        for nota, error in migration.errors:
            print(f"Error with nota {nota}:")
            print(error)
            print()

        Note.objects.filter(status_register__isnull=True)\
            .update(status_register_id="approved_v1")

