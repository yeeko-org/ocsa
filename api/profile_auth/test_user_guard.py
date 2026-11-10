"""Un usuario no se borra si algo del proyecto lo señala (task-140)."""
from datetime import date

from django.db import transaction
from django.db.models import ProtectedError
from django.test import TestCase
from rest_framework.authtoken.models import Token

from profile_auth.models import User
from source.models import Note, Source


class UserGuardTests(TestCase):

    def test_un_usuario_con_una_nota_editada_no_se_borra(self):
        user = User.objects.create_user(username="capturista", password="x")
        source = Source.objects.create(name="La Jornada")
        note = Note.objects.create(
            title="Nota", source=source, date=date(2026, 11, 9))
        note.editors.add(user)

        # pre_delete runs inside the Collector's atomic block without a
        # savepoint: each attempt needs its own to keep the test usable.
        with self.assertRaises(ProtectedError), transaction.atomic():
            user.delete()
        with self.assertRaises(ProtectedError), transaction.atomic():
            User.objects.filter(pk=user.pk).delete()
        self.assertTrue(User.objects.filter(pk=user.pk).exists())
        self.assertTrue(note.editors.filter(pk=user.pk).exists())

    def test_un_usuario_con_solo_su_token_si_se_borra(self):
        user = User.objects.create_user(username="sin_trabajo", password="x")
        Token.objects.create(user=user)

        user.delete()

        self.assertFalse(User.objects.filter(username="sin_trabajo").exists())
        self.assertFalse(Token.objects.exists())
