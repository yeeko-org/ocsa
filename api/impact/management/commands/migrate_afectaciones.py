from django.core.management.base import BaseCommand

from impact.migrate import AfectacionesToImpactMigrate
from impact.models import ImpactSubtype, ImpactType


class Command(BaseCommand):
    help = 'Migración de Modelos Legacy a Impact'

    def handle(self, *args, **kwargs):

        print("Starting Impact migration")
        afectaciones_migration = AfectacionesToImpactMigrate()

        for afectacion, error in afectaciones_migration.errors:
            print(f"Error with afectacion {afectacion.pk}: {afectacion}")
            print(error)
            print()

        ImpactType.objects.filter(status_validation__isnull=True)\
            .update(status_validation_id='original')
        ImpactSubtype.objects.filter(status_validation__isnull=True)\
            .update(status_validation_id='original')
