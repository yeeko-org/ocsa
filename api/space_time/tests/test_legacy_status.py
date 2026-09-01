"""Un estatus legacy se ve siempre, pero solo lo asigna un superusuario.

Es el tercer eje del candado, encima de `open_editor` (quién puede tocar
el registro) y de `open_selectable` (qué destino admite la captura): un
estatus retirado del flujo vivo sigue visible en los registros que ya lo
tienen, y ningún editor pleno puede mover otro hacia él (task-71).
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from profile_auth.models import User
from project.models import Project
from space_time.models import Location
from work_flux.test_helpers import make_status


class LegacyStatusTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.validation = make_status(
            name="val", group="validation", public_name="Validado")
        # Guardar una ubicación recalcula el status_location de su
        # proyecto, y sin ubicaciones con status el valor es «empty».
        make_status(
            name="empty", group="location", public_name="Sin ubicación")
        # Abierto en los otros dos ejes: así el único motivo posible de
        # un rechazo es que sea legacy.
        cls.legacy = make_status(
            name="migrado_v1", group="location", public_name="v1. Migrado",
            is_legacy=True, open_editor=True, open_selectable=True)
        cls.live = make_status(
            name="inicial", group="location", public_name="Datos iniciales",
            open_editor=True, open_selectable=True)
        cls.project = Project.objects.create(
            name="Presa", status_validation=cls.validation)
        cls.live_location = Location.objects.create(
            project=cls.project, details="viva",
            status_location=cls.live)
        cls.legacy_location = Location.objects.create(
            project=cls.project, details="heredada",
            status_location=cls.legacy)
        cls.editor = User.objects.create_user(
            username="capturista", password="x", full_editor=True)
        cls.superuser = User.objects.create_superuser(
            username="jefa", password="x")

    def _patch(self, user, location, payload):
        client = APIClient()
        client.force_authenticate(user)
        return client.patch(
            reverse("location-detail", args=[location.pk]),
            payload, format="json")

    def test_el_editor_pleno_no_puede_asignar_un_legacy(self):
        response = self._patch(
            self.editor, self.live_location,
            {"status_location": self.legacy.pk})
        self.assertEqual(response.status_code, 403, response.data)
        self.live_location.refresh_from_db()
        self.assertEqual(self.live_location.status_location_id, "inicial")

    def test_el_superusuario_si_puede_asignar_un_legacy(self):
        response = self._patch(
            self.superuser, self.live_location,
            {"status_location": self.legacy.pk})
        self.assertEqual(response.status_code, 200, response.data)
        self.live_location.refresh_from_db()
        self.assertEqual(self.live_location.status_location_id, "migrado_v1")

    def test_permanecer_en_un_legacy_no_se_bloquea(self):
        """El payload repite el status que el registro ya tiene."""
        response = self._patch(
            self.editor, self.legacy_location,
            {"status_location": self.legacy.pk, "details": "corregida"})
        self.assertEqual(response.status_code, 200, response.data)
        self.legacy_location.refresh_from_db()
        self.assertEqual(self.legacy_location.details, "corregida")
        self.assertEqual(
            self.legacy_location.status_location_id, "migrado_v1")
