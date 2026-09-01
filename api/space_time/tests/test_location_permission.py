"""El candado editorial de la ubicación vive en su status.

`LocationPermission` cierra la edición cuando el status tiene
`open_editor=False` y deja pasar a los administradores. El status es
nulable y hay filas heredadas sin él: sin status no hay candado que
aplicar, igual que en el dashboard.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from profile_auth.models import User
from project.models import Project
from space_time.models import Location
from work_flux.test_helpers import make_status


class LocationPermissionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.validation = make_status(
            name="val", group="validation", public_name="Validado")
        # Guardar una ubicación recalcula el status_location de su
        # proyecto, y sin ubicaciones con status el valor es «empty».
        make_status(
            name="empty", group="location", public_name="Sin ubicación")
        cls.closed = make_status(
            name="closed", group="location", public_name="Cerrada",
            open_editor=False)
        cls.project = Project.objects.create(
            name="Presa", status_validation=cls.validation)
        cls.orphan_status = Location.objects.create(
            project=cls.project, details="sin status")
        cls.locked = Location.objects.create(
            project=cls.project, details="cerrada",
            status_location=cls.closed)
        cls.editor = User.objects.create_user(
            username="capturista", password="x", full_editor=True)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.editor)

    def _patch(self, location):
        return self.client.patch(
            reverse("location-detail", args=[location.pk]),
            {"details": "corregida"}, format="json")

    def test_la_ubicacion_sin_status_se_edita(self):
        response = self._patch(self.orphan_status)
        self.assertEqual(response.status_code, 200, response.data)

    def test_el_status_cerrado_bloquea_a_quien_no_es_admin(self):
        response = self._patch(self.locked)
        self.assertEqual(response.status_code, 403, response.data)
