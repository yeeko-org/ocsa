"""
Cierra la sesión activa contra PressReader, liberando el slot del
lado del servidor.

Comportamiento "online-estricto": si el endpoint de signOut falla (API
caída, red, etc.), NO borra el registro local. La razón: `forceSignOut`
del próximo login no invalida tokens previos (verificado), así que
borrar local sin haber cerrado realmente dejaría una huérfana
garantizada. Mejor conservar el token y reintentar después.

Uso:
    python manage.py close_pressreader_session
"""

from django.core.management.base import BaseCommand

from source.models import PressReaderSession
from source.scraper.pressreader_auth import signout_with_token


class Command(BaseCommand):
    help = "Cierra la sesión activa de PressReader (libera slot del servidor)."

    def handle(self, *args, **options):
        session = PressReaderSession.get_active()
        if not session:
            self.stdout.write("Sin sesión activa. Nada que cerrar.")
            return

        self.stdout.write(
            f"Cerrando sesión {session.bearer_token[:40]}..."
        )
        if signout_with_token(session.bearer_token):
            session.delete()
            self.stdout.write(self.style.SUCCESS(
                "✓ Sesión cerrada y registro eliminado."
            ))
            return

        self.stdout.write(self.style.ERROR(
            "✗ SignOut falló. El registro local NO se eliminó "
            "(se conserva para reintentar más tarde)."
        ))
        self.stdout.write(
            "Si persiste, reintenta en unos minutos o investiga "
            "conectividad con PressReader."
        )