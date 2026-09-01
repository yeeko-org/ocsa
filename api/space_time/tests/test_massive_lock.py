"""El candado de registro cerrado también aplica en lote (task-99).

`massive_edit` filtra por queryset y nunca llama a `get_object()`, así
que `has_object_permission` no corre. El lote omite en silencio lo que
el usuario no podría editar uno por uno, y rederiva a mano lo que
`.update()` se salta al no pasar por `Location.save()` (adr-0027).
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from profile_auth.models import User
from project.models import Project
from space_time.models import Location
from work_flux.test_helpers import make_status


class MassiveLockTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.validation = make_status(
            name="val", group="validation", public_name="Validado")
        # `priority` decide cuál gana la herencia: el más alto es el peor.
        make_status(
            name="empty", group="location", public_name="Sin ubicación",
            priority=9)
        cls.open_status = make_status(
            name="abierta", group="location", public_name="Abierta",
            priority=1)
        cls.closed_status = make_status(
            name="cerrada", group="location", public_name="Cerrada",
            open_editor=False, priority=5)
        cls.project = Project.objects.create(
            name="Presa", status_validation=cls.validation)
        cls.open_loc = Location.objects.create(
            project=cls.project, details="abierta",
            status_location=cls.open_status)
        cls.closed_loc = Location.objects.create(
            project=cls.project, details="cerrada",
            status_location=cls.closed_status)
        cls.editor = User.objects.create_user(
            username="capturista", password="x", full_editor=True)
        cls.admin = User.objects.create_user(
            username="jefa", password="x", is_staff=True)

    def _massive(self, user, ids, payload):
        client = APIClient()
        client.force_authenticate(user)
        return client.post(
            reverse("location-massive-edit"),
            {"elems_ids": ids, **payload}, format="json")

    def test_el_lote_omite_los_registros_cerrados(self):
        response = self._massive(
            self.editor, [self.open_loc.pk, self.closed_loc.pk],
            {"details": "tocada"})
        self.assertEqual(response.status_code, 200, response.data)
        self.open_loc.refresh_from_db()
        self.closed_loc.refresh_from_db()
        self.assertEqual(self.open_loc.details, "tocada")
        self.assertEqual(self.closed_loc.details, "cerrada")

    def test_el_admin_edita_todo_el_lote(self):
        response = self._massive(
            self.admin, [self.open_loc.pk, self.closed_loc.pk],
            {"details": "tocada"})
        self.assertEqual(response.status_code, 200, response.data)
        for location in (self.open_loc, self.closed_loc):
            location.refresh_from_db()
            self.assertEqual(location.details, "tocada")

    def test_la_respuesta_solo_trae_lo_editado(self):
        response = self._massive(
            self.editor, [self.open_loc.pk, self.closed_loc.pk],
            {"details": "tocada"})
        returned = {item["id"] for item in response.data}
        self.assertEqual(returned, {self.open_loc.pk})

    def test_el_lote_rederiva_el_status_del_proyecto(self):
        """Sin el gancho, `.update()` dejaría al proyecto desfasado."""
        self.project.refresh_from_db()
        self.assertEqual(self.project.status_location_id, "cerrada")
        response = self._massive(
            self.admin, [self.closed_loc.pk],
            {"status_location": self.open_status.pk})
        self.assertEqual(response.status_code, 200, response.data)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status_location_id, "abierta")
