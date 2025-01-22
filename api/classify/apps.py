import sys
from django.apps import AppConfig


class ClassifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classify'
    verbose_name = 'Clasificaciones de actores'

    def ready(self) -> None:
        from .initial_data import (
            InitParticipantTypes, TemporalParticipantTypes, InitSectorGroups,
            InitSector, InitBelongs, InitParticipantGroups, InitInterestTypes)

        _ready = super().ready()
        valid_commands = ["migrate_initial_data", "migrate_classify"]
        if any([command in sys.argv for command in valid_commands]):
            print('Cargando datos iniciales de clasificadores de actores...')
            InitParticipantGroups()
            InitSectorGroups()
            InitParticipantTypes()
            TemporalParticipantTypes()
            InitSector()
            InitBelongs()
            InitInterestTypes()
            print('Datos iniciales cargados.')
        return _ready
