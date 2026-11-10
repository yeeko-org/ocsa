from django.apps import AppConfig


class ProfileAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile_auth'
    verbose_name = "3. Perfil y Autenticación"

    def ready(self) -> None:
        from profile_auth.signals import register_user_guard
        register_user_guard(self.get_model("User"))
