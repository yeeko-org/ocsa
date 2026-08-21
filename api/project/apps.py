from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'
    verbose_name = '5. Proyectos y Conflictos'

    def ready(self) -> None:
        import project.catalog_schema  # noqa — triggers @catalog_registry.register
        from core.file_cleanup import register_file_cleanup
        from project.models import ProjectFile
        register_file_cleanup(ProjectFile)
