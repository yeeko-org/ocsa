"""Reconstruye los índices precalculados del mapa y los deja en caché.

Pensado para el cron diario (refresca antes de que caduque el TTL de
24 h, así ningún usuario paga el costo de reconstrucción):

    python manage.py rebuild_map_index

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registradas.
"""

from django.core.management.base import BaseCommand

from api.views.map.index_cache import rebuild_all


class Command(BaseCommand):
    help = "Reconstruye y cachea los índices de facetas y actores del mapa."

    def handle(self, *args, **options) -> None:
        summary = rebuild_all()
        self.stdout.write(self.style.SUCCESS(
            f"Índices del mapa reconstruidos: "
            f"{summary['projects']} proyectos, "
            f"{summary['actors']} actores."))
