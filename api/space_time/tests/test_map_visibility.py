"""Criterio único de visibilidad del mapa público (docs `adr-0022`).

Cuida que pins, facetas y actores no vuelvan a divergir. Los helpers
que se ejercitan viven en `api/views/map/visibility.py` y se prueban
desde aquí porque `api/` no es una app instalada y el runner no
descubriría sus tests.
"""

from datetime import date

from django.test import TestCase

from actor.models import Actor, Participant
from api.views.map.visibility import (
    visible_locations, visible_mentions, visible_projects)
from project.models import Project
from source.models import Mention, Note, Source
from space_time.models import Location
from work_flux.test_helpers import make_status


class MapVisibilityTests(TestCase):
    """Un proyecto es visible si su validación es pública y tiene al
    menos una ubicación pública; una mención, si además su nota lo es."""

    @classmethod
    def setUpTestData(cls):
        cls.val_pub = make_status(
            name="val_pub", group="validation", public_name="Validado",
            is_public=True)
        cls.val_priv = make_status(
            name="val_priv", group="validation", public_name="En revisión",
            is_public=False)
        cls.loc_pub = make_status(
            name="loc_pub", group="location", public_name="Aprobada",
            is_public=True)
        cls.loc_priv = make_status(
            name="loc_priv", group="location", public_name="Inicial",
            is_public=False)
        cls.reg_pub = make_status(
            name="reg_pub", group="register", public_name="Publicada",
            is_public=True)
        cls.reg_priv = make_status(
            name="reg_priv", group="register", public_name="Capturada",
            is_public=False)

        cls.ok = cls._project("visible", cls.val_pub, [cls.loc_pub])
        cls.sin_ubicacion_publica = cls._project(
            "sin ubicación pública", cls.val_pub, [cls.loc_priv])
        cls.fantasma = cls._project(
            "fantasma", cls.val_priv, [cls.loc_pub])
        cls.multi = cls._project(
            "multiubicación", cls.val_pub, [cls.loc_pub, cls.loc_priv])
        cls.sin_ubicaciones = cls._project("sin ubicaciones", cls.val_pub, [])

        source = Source.objects.create(name="La Jornada")
        cls.nota_publica = Note.objects.create(
            title="pública", source=source, date=date(2026, 8, 26),
            status_register=cls.reg_pub)
        cls.nota_privada = Note.objects.create(
            title="privada", source=source, date=date(2026, 8, 26),
            status_register=cls.reg_priv)

        cls.mencion_ok = Mention.objects.create(
            note=cls.nota_publica, project=cls.ok)
        cls.mencion_fantasma = Mention.objects.create(
            note=cls.nota_publica, project=cls.fantasma)
        cls.mencion_nota_privada = Mention.objects.create(
            note=cls.nota_privada, project=cls.ok)

        actor = Actor.objects.create(name="Colectivo")
        cls.part_ok = Participant.objects.create(
            actor=actor, mention=cls.mencion_ok)
        cls.part_fantasma = Participant.objects.create(
            actor=actor, mention=cls.mencion_fantasma)
        cls.part_nota_privada = Participant.objects.create(
            actor=actor, mention=cls.mencion_nota_privada)

    @classmethod
    def _project(cls, name, validation, location_statuses):
        project = Project.objects.create(
            name=name, status_validation=validation)
        for status in location_statuses:
            Location.objects.create(project=project, status_location=status)
        return project

    def assertRows(self, queryset, expected):
        self.assertEqual(list(queryset.order_by("id")), expected)

    def test_validacion_y_ubicacion_publicas(self):
        self.assertIn(self.ok, visible_projects(Project.objects.all()))
        self.assertEqual(
            visible_locations(Location.objects.filter(project=self.ok))
            .count(), 1)

    def test_sin_ubicacion_publica_no_es_visible(self):
        self.assertNotIn(
            self.sin_ubicacion_publica, visible_projects(Project.objects.all()))
        self.assertFalse(visible_locations(
            Location.objects.filter(project=self.sin_ubicacion_publica)))

    def test_validacion_no_publica_oculta_el_pin(self):
        """El pin fantasma de `adr-0022`: la ubicación es pública pero
        la ficha del proyecto no está aprobada."""
        self.assertNotIn(self.fantasma, visible_projects(Project.objects.all()))
        self.assertFalse(visible_locations(
            Location.objects.filter(project=self.fantasma)))

    def test_multiubicacion_no_duplica_ni_arrastra_la_privada(self):
        visibles = visible_projects(Project.objects.filter(pk=self.multi.pk))
        self.assertEqual(visibles.count(), 1)
        ubicaciones = visible_locations(
            Location.objects.filter(project=self.multi))
        self.assertEqual(
            [loc.status_location_id for loc in ubicaciones], ["loc_pub"])

    def test_proyecto_sin_ubicaciones_no_es_visible(self):
        self.assertNotIn(
            self.sin_ubicaciones, visible_projects(Project.objects.all()))

    def test_el_mismo_veredicto_por_mencion_y_por_participacion(self):
        """Las rutas de lookup son lo que impide que los índices y los
        pins vuelvan a divergir."""
        self.assertRows(
            visible_projects(Mention.objects.all(), "project"),
            [self.mencion_ok, self.mencion_nota_privada])
        self.assertRows(
            visible_projects(Participant.objects.all(), "mention__project"),
            [self.part_ok, self.part_nota_privada])

    def test_la_nota_no_publica_sale_de_facetas_y_actores(self):
        self.assertRows(
            visible_mentions(Mention.objects.all()), [self.mencion_ok])
        self.assertRows(
            visible_mentions(Participant.objects.all(), "mention"),
            [self.part_ok])
