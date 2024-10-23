import sys
from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "event"

    def ready(self) -> None:
        from .models import InvolvedRole
        _ready = super().ready()
        init_involved_roles = [
            "Victimario",
            "Responsable",
            "Víctima",
            "Accionante"]

        valid_commands = ["runserver", "migrate_eventos"]
        if any([command in sys.argv for command in valid_commands]):
            print('Cargando datos iniciales de InvolvedRole...')
            for role in init_involved_roles:
                InvolvedRole.objects.get_or_create(name=role)
            print("Datos iniciales cargados.")

        return _ready
