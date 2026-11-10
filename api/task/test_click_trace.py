"""El historial de clics no se borra con lo que registra (task-140).

Borrar un proyecto arrastra sus ubicaciones en cascada; los clics de los
dos sobreviven con la llave en nulo y el rastro en `deleted_origin`, que en
las ubicaciones lleva además el id y el nombre de su proyecto.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from profile_auth.models import User
from project.models import Project
from space_time.models import Location
from task.models import ClickHistory


class ClickTraceTests(TestCase):

    def test_borrar_un_proyecto_conserva_sus_clics_y_los_de_sus_ubicaciones(
            self):
        user = User.objects.create_user(username="capturista", password="x")
        project = Project.objects.create(name="Tren Maya")
        location = Location.objects.create(
            project=project, latitude=20.5, longitude=-87.3)
        on_project = ClickHistory.objects.create(
            user=user, action="opened", project=project)
        on_location = ClickHistory.objects.create(
            user=user, action="updated", location=location)
        # Borrada sola, sin cascada: el nombre del proyecto se consulta.
        alone = Location.objects.create(project=project, details="Mina")
        on_alone = ClickHistory.objects.create(
            user=user, action="updated", location=alone)
        project_id, location_id = project.id, location.id

        alone.delete()
        project.delete()

        on_project.refresh_from_db()
        on_location.refresh_from_db()
        self.assertIsNone(on_project.project_id)
        self.assertIsNone(on_location.location_id)
        self.assertEqual(
            {k: on_project.deleted_origin[k] for k in ("model", "id", "label")},
            {"model": "project", "id": project_id, "label": "Tren Maya"})
        self.assertEqual(
            {k: on_location.deleted_origin[k]
             for k in ("model", "id", "label")},
            {"model": "location", "id": location_id,
             "label": "20.5, -87.3"})
        self.assertIn("date", on_location.deleted_origin)
        on_alone.refresh_from_db()
        for click in (on_location, on_alone):
            self.assertEqual(
                {k: click.deleted_origin[k]
                 for k in ("project_id", "project_name")},
                {"project_id": project_id, "project_name": "Tren Maya"})
        self.assertNotIn("project_id", on_project.deleted_origin)

    def test_guardar_un_proyecto_deja_un_clic(self):
        user = User.objects.create_user(
            username="capturista", password="x", full_editor=True)
        project = Project.objects.create(name="Tren Maya")
        client = APIClient()
        client.force_authenticate(user)

        res = client.patch(
            reverse("project-detail", args=[project.pk]),
            {"name": "Tren Maya, tramo 5"}, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            list(ClickHistory.objects.values_list(
                "project_id", "action", "user_id")),
            [(project.id, "updated", user.id)])
