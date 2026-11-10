"""El propósito solo vive en los mecanismos legales (task-125).

Protege `EventMediumSerializer.validate`: un evento que deja de ser
mecanismo legal pierde su propósito, y editar uno legal no lo toca.
"""
from datetime import date

from django.test import TestCase

from api.views.event.serializers import EventMediumSerializer
from event.models import Event, EventGroup, EventType, Purpose
from project.models import Project
from source.models import Mention, Note, Source


class PurposeOnlyOnLegalTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        legal = EventGroup.objects.create(
            name="Mecanismos legales", show_position=True)
        other = EventGroup.objects.create(name="Acciones colectivas")
        cls.legal_type = EventType.objects.create(
            name="Amparo", event_group=legal)
        cls.other_type = EventType.objects.create(
            name="Marcha", event_group=other)
        cls.purpose = Purpose.objects.create(name="Defensa")
        note = Note.objects.create(
            title="Nota", source=Source.objects.create(name="La Jornada"),
            date=date(2026, 11, 9))
        mention = Mention.objects.create(
            note=note, project=Project.objects.create(name="Mina"))
        cls.event = Event.objects.create(
            mention=mention, event_type=cls.legal_type,
            purpose=cls.purpose)

    def save(self, data: dict) -> Event:
        serializer = EventMediumSerializer(
            self.event, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def test_cambiar_a_otro_tipo_limpia_el_proposito(self):
        event = self.save({"event_type": self.other_type.id})
        event.refresh_from_db()
        self.assertIsNone(event.purpose_id)

    def test_editar_un_mecanismo_legal_conserva_el_proposito(self):
        event = self.save({"description": "Amparo admitido"})
        event.refresh_from_db()
        self.assertEqual(event.purpose_id, self.purpose.id)
