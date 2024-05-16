import sys
from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event"

    def ready(self) -> None:
        from .models import init_event_roles, EventRole
        _ready = super().ready()

        valid_commands = ["runserver", "migrate_eventos"]
        if any([command in sys.argv for command in valid_commands]):
            print('Cargando datos iniciales de EventRole...')
            for role in init_event_roles:
                EventRole.objects.get_or_create(name=role)
            print("Datos iniciales cargados.")

        return _ready
