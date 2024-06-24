import sys
from django.apps import AppConfig


class ClassifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classify'
    verbose_name = 'Clasificaciones de actores'

    def ready(self) -> None:
        from .initial_data import (
            ParticipantTypes, TemporalParticipantTypes, InitSectorGroups, InitSector, InitBelongs)
        from work_flux.initial_data import InitStatus
        _ready = super().ready()
        valid_commands = ["runserver", "migrate_classify"]
        if any([command in sys.argv for command in valid_commands]):
            print('Cargando datos iniciales de clasificadores de actores...')
            InitStatus()
            ParticipantTypes()
            InitSectorGroups()
            TemporalParticipantTypes()
            InitSector()
            InitBelongs()
            print('Datos iniciales cargados.')
        return _ready
