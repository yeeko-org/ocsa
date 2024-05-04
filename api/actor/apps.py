import sys
from django.apps import AppConfig


class ActorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actor'
    verbose_name = 'Actores'

    def ready(self) -> None:
        from .initial_data import ParticipantTypes, TemporalParticipantTypes
        _ready = super().ready()
        if 'runserver' in sys.argv:
            print('Cargando datos iniciales...')
            ParticipantTypes()
            TemporalParticipantTypes()
            print('Datos iniciales cargados.')
        return _ready
