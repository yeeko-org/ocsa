"""Reclasifica con IA los eventos que quedaron en «Mecanismos legales».

Dos pasos, ambos idempotentes:

  1. backfill — marca `reclassification_stage='pending'` los eventos cuyo
     tipo sigue en `need_reclassify` y aún no tienen etapa. No toca los
     ya reclasificados, confirmados o descartados.
  2. run      — reclasifica con Gemini los pendientes.

    python manage.py reclassify_legal_events
    python manage.py reclassify_legal_events --only-backfill

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registradas.
"""

from django.core.management.base import BaseCommand

from event.models import Event
from source.criteria.reclassify_legal import ReclassifyLegalManager


class Command(BaseCommand):
    help = "Marca y reclasifica los eventos pendientes de mecanismo legal."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--only-backfill", action="store_true",
            help="Solo marca pendientes, sin llamar a la IA.")

    def handle(self, *args, **options) -> None:
        marked = Event.objects.filter(
            event_type__status_validation_id="need_reclassify",
            reclassification_stage__isnull=True,
        ).update(reclassification_stage="pending")
        self.stdout.write(f"Eventos marcados como pending: {marked}")

        if options["only_backfill"]:
            return

        ReclassifyLegalManager().build_criteria()
