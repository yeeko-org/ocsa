"""La ubicación siempre cuelga de una ficha, salvo en lote.

Una ubicación sin proyecto, evento ni impacto no se lista ni se alcanza
desde ninguna ficha: nace huérfana y nadie la corrige. El serializer la
rechaza en toda escritura de detalle; la edición masiva queda fuera
porque su payload trae solo los campos editados.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from api.views.space_time.serializers import LocationSerializer
from profile_auth.models import User
from project.models import Project
from space_time.models import Location, State
from work_flux.test_helpers import make_status


class LocationOwnerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.validation = make_status(
            name="val", group="validation", public_name="Validado")
        # Guardar una ubicación recalcula el status_location de su
        # proyecto, y sin ubicaciones con status el valor es «empty».
        make_status(
            name="empty", group="location", public_name="Sin ubicación")
        cls.project = Project.objects.create(
            name="Presa", status_validation=cls.validation)
        cls.state = State.objects.create(inegi_code="99", name="Sintética")
        cls.other_state = State.objects.create(
            inegi_code="98", name="Ajena")
        cls.first = Location.objects.create(
            project=cls.project, details="primera", state=cls.state)
        cls.second = Location.objects.create(
            project=cls.project, details="segunda", state=cls.state)
        cls.user = User.objects.create_user(
            username="capturista", password="x", full_editor=True)

    def test_la_ubicacion_sin_dueno_se_rechaza(self):
        serializer = LocationSerializer(data={"details": "suelta"})
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Una ubicación debe pertenecer a un proyecto, un evento "
            "o un impacto.",
            [str(error) for error in serializer.errors["non_field_errors"]])

    def test_el_patch_parcial_no_pide_el_dueno_de_nuevo(self):
        """El dueño ya está en la instancia: el payload no lo repite."""
        serializer = LocationSerializer(
            self.first, data={"details": "corregida"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_la_edicion_masiva_no_pide_dueno(self):
        client = APIClient()
        client.force_authenticate(self.user)
        response = client.post(
            reverse("location-massive-edit"),
            {"elems_ids": [self.first.pk, self.second.pk],
             "state": self.other_state.pk}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        for location in (self.first, self.second):
            location.refresh_from_db()
            self.assertEqual(location.state, self.other_state)
            self.assertEqual(location.project, self.project)
