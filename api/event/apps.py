import sys
from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event"

    def ready(self) -> None:
        from .models import init_event_roles, EventRole
        _ready = super().ready()
        print('Cargando datos iniciales de EventRole...')
        if [command in sys.argv for command in ["runserver", "migrate_eventos"]]:
            for role in init_event_roles:
                EventRole.objects.get_or_create(name=role)
            print("Datos iniciales cargados.")
        return _ready
