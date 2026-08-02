"""Recupera el histórico de «Editorial» y «El Correo Ilustrado».

Esas dos secciones de La Jornada nunca entraron por scraping porque su
URL sirve el artículo y no un listado. El arreglo de [[adr-0004]] las
captura hacia adelante; este comando recupera lo que quedó atrás.

Trabaja lote por lote y de forma idempotente: re-correrlo no duplica
artículos ni vuelve a pagar scraping ni clasificación de lo ya hecho.

    python manage.py recover_single_sections --phase scrape --limit-records 1
    python manage.py recover_single_sections --limit-records 1 --user ricardo@…
    python manage.py recover_single_sections

`--phase scrape` no gasta cuota de Gemini: sirve para verificar el HTML
extraído antes de pagar la clasificación.

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registradas.
"""

from django.core.management.base import BaseCommand

from profile_auth.models import User
from source.scraper.recover_sections import SingleSectionRecovery


class Command(BaseCommand):
    help = "Recupera los artículos históricos de las secciones de "\
           "artículo único de La Jornada."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--phase", choices=["scrape", "classify", "all"], default="all",
            help="Fase a ejecutar (default: todas).")
        parser.add_argument(
            "--limit-records", type=int, default=None,
            help="Tope de lotes, para una corrida de prueba.")
        parser.add_argument(
            "--user", type=str, default=None,
            help="Email del editor al que se asignan las notas nuevas.")
        parser.add_argument(
            "--engine", type=str, default=None,
            help="Motor de Gemini; por defecto, el de settings.")

    def handle(self, *args, **options) -> None:
        user = None
        if options["user"]:
            user = User.objects.filter(email=options["user"]).first()
            if not user:
                self.stderr.write(
                    f"No existe el usuario {options['user']}")
                return

        SingleSectionRecovery(
            limit_records=options["limit_records"],
            phase=options["phase"],
            user=user,
            ai_engine=options["engine"],
        ).run()
