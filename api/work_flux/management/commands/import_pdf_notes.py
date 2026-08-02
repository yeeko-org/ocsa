"""Rescata notas legadas guardadas como PDF, anteriores al scraping.

Dos fases independientes e idempotentes; re-correr no duplica ni
reprocesa, así que se pueden lanzar por separado o encadenadas:

  1. extract — descarga el PDF y extrae el crudo a `Article.html_content`
  2. clean   — limpia ese crudo con Gemini a `Article.paragraphs`

    python manage.py import_pdf_notes                 # ambas fases
    python manage.py import_pdf_notes --phase extract --limit 20
    python manage.py import_pdf_notes --phase clean

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registadas.
"""

from django.core.management.base import BaseCommand

from source.pdf_import.clean import PdfAiCleaner
from source.pdf_import.extract import PdfTextExtractor


class Command(BaseCommand):
    help = "Extrae y limpia el contenido de notas legadas en PDF."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--phase", choices=["extract", "clean", "all"], default="all",
            help="Fase a ejecutar (default: ambas).")
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Tope de registros por fase, para una corrida de prueba.")

    def handle(self, *args, **options) -> None:
        phase = options["phase"]
        limit = options["limit"]

        if phase in ("extract", "all"):
            self.stdout.write("Fase 1: extracción del crudo")
            PdfTextExtractor().run(limit)

        if phase in ("clean", "all"):
            self.stdout.write("Fase 2: limpieza asistida por IA")
            PdfAiCleaner().run(limit)
