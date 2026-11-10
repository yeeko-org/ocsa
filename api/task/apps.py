from django.apps import AppConfig


class TaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task'
    verbose_name = "4. Gestión de tareas"

    def ready(self) -> None:
        from task.signals import register_click_trace
        register_click_trace()
