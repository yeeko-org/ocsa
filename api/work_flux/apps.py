import sys
from django.apps import AppConfig


class WorkFluxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'work_flux'
    verbose_name = '2. Flujo de trabajo'

    def ready(self) -> None:
        from .initial_data import InitStatus
        _ready = super().ready()
        if 'migrate_initial_data' in sys.argv:
            print('Cargando datos iniciales de work_flux...')
            InitStatus()
            print('Datos iniciales cargados.')
        return _ready
