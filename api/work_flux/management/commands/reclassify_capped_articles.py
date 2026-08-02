"""Reclasifica los artículos vetados por el criterio viejo de banderas.

Universo: `certainty_degree in (97, 98)`, los capados por opinión
política o por extranjería. Se reclasifican con el criterio de
[[adr-0006]] y el motor de [[adr-0007]], y se reporta el movimiento en
ambas direcciones.

    python manage.py reclassify_capped_articles --limit 20 --only-first
    python manage.py reclassify_capped_articles

Sobrescribe `criteria` y `certainty_degree` sin guardar el valor
anterior: la corrida no es reversible salvo re-clasificando con el
prompt viejo.

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registradas.
"""

from django.core.management.base import BaseCommand

from source.criteria.reclassify_capped import CappedReclassifier


class Command(BaseCommand):
    help = "Reclasifica los artículos capados a 97/98 con el criterio nuevo."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Tope de artículos, para una corrida de prueba.")
        parser.add_argument(
            "--chunk-size", type=int, default=60,
            help="Artículos por caché de contexto (default: 60).")
        parser.add_argument(
            "--only-first", action="store_true",
            help="Omite la segunda pasada sobre los que superen 100.")
        parser.add_argument(
            "--engine", type=str, default=None,
            help="Motor de Gemini; por defecto, el de settings.")

    def handle(self, *args, **options) -> None:
        CappedReclassifier(
            chunk_size=options["chunk_size"],
            limit=options["limit"],
            only_first=options["only_first"],
            ai_engine=options["engine"],
        ).run()
