"""Catálogo del INPI en IndigenousGroup: carga, fusión y búsqueda.

Lo que se protege es lo que no se deshace solo: que repetir la carga o la
fusión no duplique ni reescriba nada, que solo el homónimo del nombre o de
sus partes se adopte (cualquier otro autónimo es una fusión), que fusionar
no pierda el nombre absorbido, y que el catálogo se encuentre por sus
nombres alternativos.
"""
import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from actor.models import Actor
from classify.models import IndigenousGroup
from profile_auth.models import User
from space_time.models import State
from utils.register_merge import RecordMerger
from work_flux.test_helpers import make_status


def pueblo(dof_name, autonym=None, alternatives=()):
    name = f"{autonym} ({dof_name})" if autonym else dof_name
    return {
        "name": name, "dof_name": dof_name, "autonym": autonym,
        "microsite_name": dof_name,
        "alternative_names": [n for n in (autonym, dof_name, *alternatives)
                              if n and n != name],
    }


PUEBLOS = [
    pueblo("Mixe", "Ayuuk", ["Ayuujk", "Ayook"]),
    pueblo("Huichol", "Wixárika", ["Wixaritari"]),
    pueblo("Zapoteco", "Binnizá", ["Zapoteca"]),
]
STATES = {
    "Mixe": {"states": {"Oaxaca": 157}},
    "Huichol": {"states": {"Jalisco": 30, "Nayarit": 20}},
}


class InpiCatalogTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.original = make_status(
            name="original", group="validation", public_name="Original")
        make_status(
            name="validated", group="validation", public_name="Aprobado")
        make_status(
            name="expired", group="validation", public_name="Caducado")
        make_status(
            name="could_reclassify", group="validation",
            public_name="Podría reclasificarse")
        for code, name in [("20", "Oaxaca"), ("14", "Jalisco"),
                           ("18", "Nayarit")]:
            State.objects.create(inegi_code=code, name=name, short_name=name)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name) / "pueblos.json"
        cls.path.write_text(
            json.dumps({"pueblos": PUEBLOS}), encoding="utf-8")
        cls.states_path = Path(cls.tmp.name) / "estados.json"
        cls.states_path.write_text(
            json.dumps({"pueblos": STATES}), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
        super().tearDownClass()

    def call(self, command, *args):
        out = StringIO()
        call_command(command, "--path", str(self.path), *args, stdout=out)
        return out.getvalue()

    def load(self):
        return self.call(
            "load_inpi_catalog", "--states-path", str(self.states_path))

    def snapshot(self):
        groups = list(IndigenousGroup.objects.order_by("id").values_list(
            "id", "name", "alternative_names", "is_official",
            "status_validation_id", "comments"))
        states = sorted(IndigenousGroup.states.through.objects.values_list(
            "indigenousgroup_id", "state_id"))
        actors = list(Actor.objects.order_by("id").values_list(
            "id", "indigenous_group_id", "comments"))
        return groups, states, actors


class LoadInpiCatalogTests(InpiCatalogTestCase):

    def test_repetir_la_carga_no_crea_ni_cambia_nada(self):
        IndigenousGroup.objects.create(
            name="Mixe", status_validation=self.original)
        self.load()
        first = self.snapshot()
        output = self.load()
        self.assertEqual(self.snapshot(), first)
        self.assertIn("0 creados, 3 adoptados (0 con cambios)", output)
        self.assertIn("0 estados agregados", output)
        mixe = IndigenousGroup.objects.get(name="Ayuuk (Mixe)")
        self.assertEqual(
            list(mixe.states.values_list("name", flat=True)), ["Oaxaca"])

    def test_adopta_el_homonimo_y_no_toca_el_autonimo(self):
        # «Mixe» es la denominación del DOF, una de las dos partes del
        # nombre: se adopta. «Ayuujk» es otra autodenominación: no.
        mixe = IndigenousGroup.objects.create(
            name="Mixe", status_validation=self.original)
        ayuujk = IndigenousGroup.objects.create(
            name="Ayuujk", status_validation=self.original)
        actor = Actor.objects.create(name="Asamblea", indigenous_group=ayuujk)

        self.load()

        mixe.refresh_from_db()
        self.assertEqual(mixe.name, "Ayuuk (Mixe)")
        self.assertTrue(mixe.is_official)
        self.assertEqual(mixe.status_validation_id, "validated")
        self.assertIn("Ayuujk", mixe.alternative_names)

        before = (ayuujk.name, ayuujk.alternative_names, ayuujk.is_official,
                  ayuujk.status_validation_id)
        ayuujk.refresh_from_db()
        self.assertEqual(
            (ayuujk.name, ayuujk.alternative_names, ayuujk.is_official,
             ayuujk.status_validation_id), before)
        actor.refresh_from_db()
        self.assertEqual(actor.indigenous_group_id, ayuujk.id)

    def test_el_autonimo_solo_no_se_adopta(self):
        # Sin homónimo, «Ayuujk» sigue igual y el pueblo nace aparte:
        # pasarle sus actores es una fusión.
        ayuujk = IndigenousGroup.objects.create(
            name="Ayuujk", status_validation=self.original)
        self.load()
        ayuujk.refresh_from_db()
        self.assertEqual(ayuujk.name, "Ayuujk")
        self.assertFalse(ayuujk.is_official)
        self.assertEqual(ayuujk.status_validation_id, "original")
        mixe = IndigenousGroup.objects.get(name="Ayuuk (Mixe)")
        self.assertNotEqual(mixe.id, ayuujk.id)
        self.assertTrue(mixe.is_official)


class MergeIndigenousGroupsTests(InpiCatalogTestCase):

    def test_repetir_la_fusion_no_cambia_nada(self):
        mixe = IndigenousGroup.objects.create(
            name="Mixe", status_validation=self.original)
        actor = Actor.objects.create(name="Asamblea", indigenous_group=mixe)
        IndigenousGroup.objects.create(
            name="Ayuuk", status_validation=self.original)
        self.load()  # adopta «Ayuuk»; «Mixe» queda para fusionarse
        official = IndigenousGroup.objects.get(name="Ayuuk (Mixe)")

        self.call("merge_indigenous_groups")
        first = self.snapshot()
        output = self.call("merge_indigenous_groups")

        self.assertEqual(self.snapshot(), first)
        self.assertIn("0 fusionadas, 1 ya estaban", output)
        actor.refresh_from_db()
        self.assertEqual(actor.indigenous_group_id, official.id)
        mixe.refresh_from_db()
        self.assertEqual(mixe.status_validation_id, "expired")
        self.assertIn(f"fusionada en #{official.id}", mixe.comments)
        self.assertIn("Mixe", official.alternative_names)


class DashboardMergeTests(InpiCatalogTestCase):

    def test_la_fusion_pasa_el_nombre_absorbido_a_los_alternativos(self):
        main = IndigenousGroup.objects.create(
            name="Wixárika (Huichol)", alternative_names="Wixárika")
        absorbed = IndigenousGroup.objects.create(
            name="Wirrárika", alternative_names="Wixaritari, Wixárika")
        actor = Actor.objects.create(name="Consejo", indigenous_group=absorbed)

        merger = RecordMerger("classify.IndigenousGroup")
        merger.merge_registers(main.id, absorbed.id, delete_merge=True)

        self.assertEqual(merger.errors, [])
        main.refresh_from_db()
        self.assertEqual(
            main.alternative_names, "Wixárika, Wirrárika, Wixaritari")
        actor.refresh_from_db()
        self.assertEqual(actor.indigenous_group_id, main.id)


class IndigenousGroupSearchTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # La base de test nace sin extensiones y UnaccentSearchFilter
        # busca con unaccent__icontains.
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
        cls.wixarika = IndigenousGroup.objects.create(
            name="Wixárika (Huichol)", alternative_names="Wixaritari",
            is_official=True)
        IndigenousGroup.objects.create(name="Mixe", alternative_names="Ayuuk")
        cls.editor = User.objects.create_user(
            username="capturista", password="x", full_editor=True)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.editor)

    def search(self, query):
        response = self.client.get(
            reverse("catalog_indigenous_group-list"), {"q": query})
        self.assertEqual(response.status_code, 200, response.data)
        rows = response.data.get("results", response.data)
        return [row["id"] for row in rows]

    def test_encuentra_por_nombre_alternativo(self):
        self.assertEqual(self.search("wixaritari"), [self.wixarika.id])
