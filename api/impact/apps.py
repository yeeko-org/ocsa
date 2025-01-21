import sys
from django.apps import AppConfig


class ImpactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'impact'
    verbose_name = 'Afectaciones sociales y ambientales'

    def ready(self) -> None:
        from .initial_data import InitialImpactGroups
        _ready = super().ready()
        valid_commands = ["migrate_initial_data", "migrate_classify"]
        if any([command in sys.argv for command in valid_commands]):
            print('Cargando datos iniciales de impactos...')
            InitialImpactGroups()
            print('Datos iniciales cargados.')
        return _ready
