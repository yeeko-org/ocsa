from django.apps import AppConfig


class SourceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = '1. Fuentes de información'
    name = 'source'

    def ready(self):
        import source.catalog_schema  # noqa — triggers @catalog_registry.register
