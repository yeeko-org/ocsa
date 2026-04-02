import sys
from django.apps import AppConfig


class ActorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actor'
    verbose_name = 'Actores'

    def ready(self):
        import actor.catalog_schema  # noqa — triggers registry.register
