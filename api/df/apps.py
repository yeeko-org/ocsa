from django.apps import AppConfig


class DfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'df'

    def ready(self):
        import df.catalog_schema  # noqa — triggers @catalog_registry.register
