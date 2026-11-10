"""La fusión del dashboard: qué traslada y a quién se la niega (task-140).

Solo los muchos a muchos que el schema declara en `merge_carries` pasan
de la absorbida al destino (hoy, los editores del proyecto); los demás se
pierden con ella. Y el endpoint no escribe nada si el modelo no admite
fusiones o si el usuario no podría borrar la entrada absorbida.
"""
from unittest import mock

from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from actor.models import Actor
from classify.models import (
    Belong, Country, IndigenousGroup, ParticipantGroup)
from profile_auth.models import User
from project.models import Project
from space_time.models import Location
from utils.register_merge import RecordMerger
from work_flux.test_helpers import make_status


class MergeTests(TestCase):

    def test_la_fusion_traslada_editores_y_nada_mas(self):
        ana = User.objects.create_user(username="ana", password="x")
        beto = User.objects.create_user(username="beto", password="x")
        main = Project.objects.create(name="Tren")
        absorbed = Project.objects.create(name="Tren Maya")
        main.editors.add(ana)
        absorbed.editors.add(beto)

        merger = RecordMerger("project.Project")
        merger.merge_registers(main.id, absorbed.id)

        self.assertEqual(merger.errors, [])
        self.assertEqual(
            set(main.editors.values_list("username", flat=True)),
            {"ana", "beto"})

        country = Country.objects.create(name="Canadá")
        belong = Belong.objects.create(short_name="Emp.", name="Empresa")
        actor_main = Actor.objects.create(name="Minera")
        actor_absorbed = Actor.objects.create(name="Minera S. A.")
        actor_absorbed.countries.add(country)
        actor_absorbed.belongs.add(belong)

        merger = RecordMerger("actor.Actor")
        merger.merge_registers(actor_main.id, actor_absorbed.id)

        self.assertEqual(merger.errors, [])
        self.assertFalse(Actor.objects.filter(pk=actor_absorbed.pk).exists())
        self.assertFalse(actor_main.countries.exists())
        self.assertFalse(actor_main.belongs.exists())

    def test_fusionar_paises_mueve_sus_actores_sin_duplicar(self):
        main = Country.objects.create(name="México")
        absorbed = Country.objects.create(name="Mexico")
        only_absorbed = Actor.objects.create(name="Minera")
        only_main = Actor.objects.create(name="Ejido")
        both = Actor.objects.create(name="Asamblea")
        only_absorbed.countries.add(absorbed)
        only_main.countries.add(main)
        both.countries.add(main, absorbed)

        merger = RecordMerger("classify.Country")
        merger.merge_registers(main.id, absorbed.id)

        self.assertEqual(merger.errors, [])
        self.assertFalse(Country.objects.filter(pk=absorbed.pk).exists())
        through = Actor.countries.through.objects
        for actor in (only_absorbed, only_main, both):
            self.assertEqual(
                list(through.filter(actor=actor).values_list(
                    "country_id", flat=True)),
                [main.id])

    def test_el_endpoint_rechaza_sin_rol_y_modelo_sin_fusion(self):
        url = reverse("generic-merge")
        client = APIClient()
        main = Project.objects.create(name="Presa")
        absorbed = Project.objects.create(name="Presa El Zapotillo")
        editor = User.objects.create_user(username="beto", password="x")
        absorbed.editors.add(editor)

        client.force_authenticate(
            User.objects.create_user(username="sin_rol", password="x"))
        res = client.post(url, {
            "model_name": "project.Project",
            "main_id": main.id, "merge_id": absorbed.id}, format="json")

        self.assertEqual(res.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=absorbed.pk).exists())
        self.assertFalse(main.editors.exists())

        group_main = ParticipantGroup.objects.create(name="Gobierno")
        group_absorbed = ParticipantGroup.objects.create(name="Gobiernos")
        client.force_authenticate(User.objects.create_user(
            username="capturista", password="x", full_editor=True))
        res = client.post(url, {
            "model_name": "classify.ParticipantGroup",
            "main_id": group_main.id, "merge_id": group_absorbed.id},
            format="json")

        self.assertEqual(res.status_code, 403)
        self.assertIn("no admite fusiones", res.json()["errors"][0])
        self.assertTrue(
            ParticipantGroup.objects.filter(pk=group_absorbed.pk).exists())

    def test_si_falla_el_borrado_la_fusion_no_deja_nada(self):
        # The merge's own atomic block is a savepoint inside the test's
        # transaction, so its rollback leaves the asserts below valid.
        url = reverse("generic-merge")
        client = APIClient()
        client.force_authenticate(User.objects.create_user(
            username="admin", password="x", is_staff=True))
        status = make_status("Abierto", "validation", open_editor=True)
        # Saving a location rederives its project's `status_location`.
        make_status(
            name="empty", group="location", public_name="Sin ubicación")
        main = Project.objects.create(name="Presa", status_validation=status)
        absorbed = Project.objects.create(
            name="Presa El Zapotillo", status_validation=status)
        absorbed.editors.add(
            User.objects.create_user(username="beto", password="x"))
        location = Location.objects.create(project=absorbed)
        pueblo = IndigenousGroup.objects.create(
            name="Ayuuk (Mixe)", alternative_names="Ayuujk",
            status_validation=status)
        absorbed_group = IndigenousGroup.objects.create(
            name="Mixes", status_validation=status)
        actor = Actor.objects.create(
            name="Asamblea", indigenous_group=absorbed_group)

        cases = [
            (Project, "project.Project", main, absorbed),
            (IndigenousGroup, "classify.IndigenousGroup", pueblo,
             absorbed_group),
        ]
        for model, model_name, survivor, entry in cases:
            protected = ProtectedError("protegida", set())
            with mock.patch.object(model, "delete", side_effect=protected):
                res = client.post(url, {
                    "model_name": model_name, "main_id": survivor.id,
                    "merge_id": entry.id, "delete_merge": True},
                    format="json")
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()["deleted"], {})
            self.assertTrue(model.objects.filter(pk=entry.pk).exists())

        location.refresh_from_db()
        self.assertEqual(location.project_id, absorbed.id)
        self.assertFalse(main.editors.exists())
        actor.refresh_from_db()
        self.assertEqual(actor.indigenous_group_id, absorbed_group.id)
        pueblo.refresh_from_db()
        self.assertEqual(pueblo.alternative_names, "Ayuujk")
