"""Qué ve el visitante del mapa y qué le falta a una ubicación.

Dos suites que comparten la misma bandera `is_public` del status:

- ``MapVisibilityTests`` cuida que pins, facetas y actores no vuelvan a
  divergir (docs `adr-0022`). Sus helpers viven en
  ``api/views/map/visibility.py`` y se prueban aquí porque ``api/`` no
  es una app instalada y el runner no descubre sus tests.
- ``PendingFiltersTests`` cuida los filtros «Pendientes de ubicación»
  de ``space_time/completeness.py`` (task-69).
"""

from datetime import date

from django.test import TestCase

from actor.models import Actor, Participant
from api.views.map.visibility import (
    visible_locations, visible_mentions, visible_projects)
from project.models import Project
from source.models import Mention, Note, Source
from space_time.completeness import (
    ANY_PENDING, COMPLETE_UNAPPROVED, LOCATION_OPTIONS, NO_APPROVED_LOCATION,
    NO_GEOMETRY, NO_MUNICIPALITY, location_pending_q, project_pending_q)
from space_time.models import Location, Municipality, State
from work_flux.models import StatusControl


class MapVisibilityTests(TestCase):
    """Un proyecto es visible si su validación es pública y tiene al
    menos una ubicación pública; una mención, si además su nota lo es."""

    @classmethod
    def setUpTestData(cls):
        cls.val_pub = StatusControl.objects.create(
            name="val_pub", group="validation", public_name="Validado",
            is_public=True)
        cls.val_priv = StatusControl.objects.create(
            name="val_priv", group="validation", public_name="En revisión",
            is_public=False)
        cls.loc_pub = StatusControl.objects.create(
            name="loc_pub", group="location", public_name="Aprobada",
            is_public=True)
        cls.loc_priv = StatusControl.objects.create(
            name="loc_priv", group="location", public_name="Inicial",
            is_public=False)
        cls.reg_pub = StatusControl.objects.create(
            name="reg_pub", group="register", public_name="Publicada",
            is_public=True)
        cls.reg_priv = StatusControl.objects.create(
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


class PendingFiltersTests(TestCase):
    """Filtros «Pendientes de ubicación» (task-69, `completeness.py`).

    Dos invariantes: lo que se ve en la lista de ubicaciones y lo que se
    ve en la de proyectos responden a la misma pregunta, y
    `any_pending` es exactamente la unión de las demás opciones —no una
    aproximación que coincida con los datos de hoy.
    """

    @classmethod
    def setUpTestData(cls):
        cls.aprobado = StatusControl.objects.create(
            name="aprobado", group="location", public_name="Aprobada",
            is_public=True)
        cls.inicial = StatusControl.objects.create(
            name="inicial", group="location", public_name="Inicial",
            is_public=False)

        cls.state = State.objects.create(inegi_code="20", name="Oaxaca")
        cls.municipality = Municipality.objects.create(
            inegi_code="20043", complete_code="20043", name="Juchitán",
            std_name="juchitan", state=cls.state)

        cls.limpio = cls._project("limpio")
        cls._location(cls.limpio, cls.aprobado)

        cls.sin_marca = cls._project("sin marca")
        cls._location(cls.sin_marca, cls.aprobado, lat=None, lon=None)

        cls.sin_municipio = cls._project("sin municipio")
        cls._location(cls.sin_municipio, cls.aprobado, municipality=None)

        cls.sin_aprobar = cls._project("sin aprobar")
        cls._location(cls.sin_aprobar, cls.inicial)

        cls.sin_ubicaciones = cls._project("sin ubicaciones")

        # El caso que distingue una unión real de un OR que Django reancla
        # a la ubicación unida: una ubicación limpia y aprobada, y otra sin
        # aprobar que no cae en ningún cajón —tiene marca y municipio, pero
        # le falta la entidad, así que tampoco está completa.
        cls.mixto = cls._project("mixto")
        cls._location(cls.mixto, cls.aprobado)
        cls._location(cls.mixto, cls.inicial, state=None)

        # Las ubicaciones de evento o impacto no se capturan: ninguna
        # opción debe recogerlas por incompletas que estén.
        cls.huerfana = Location.objects.create(status_location=cls.inicial)

    @classmethod
    def _project(cls, name):
        return Project.objects.create(name=name)

    @classmethod
    def _location(cls, project, status, state=-1, municipality=-1,
                  lat=1.0, lon=1.0):
        return Location.objects.create(
            project=project, status_location=status,
            state=cls.state if state == -1 else state,
            municipality=cls.municipality if municipality == -1
            else municipality,
            latitude=lat, longitude=lon)

    def locations_for(self, option):
        return set(Location.objects.filter(
            location_pending_q(option)).values_list("project_id", flat=True))

    def projects_for(self, option):
        return set(Project.objects.filter(
            project_pending_q(option)).values_list("id", flat=True))

    def test_cada_opcion_dice_lo_mismo_en_ubicaciones_y_en_proyectos(self):
        for option in LOCATION_OPTIONS:
            with self.subTest(option=option):
                self.assertEqual(
                    self.locations_for(option), self.projects_for(option))

    def test_cada_opcion_recoge_el_proyecto_que_le_toca(self):
        self.assertEqual(self.projects_for(NO_GEOMETRY),
                         {self.sin_marca.pk})
        self.assertEqual(self.projects_for(NO_MUNICIPALITY),
                         {self.sin_municipio.pk})
        self.assertEqual(self.projects_for(COMPLETE_UNAPPROVED),
                         {self.sin_aprobar.pk})

    def test_sin_ubicaciones_cuenta_como_sin_ninguna_aprobada(self):
        self.assertEqual(
            self.projects_for(NO_APPROVED_LOCATION),
            {self.sin_aprobar.pk, self.sin_ubicaciones.pk})

    def test_any_pending_es_la_union_exacta_de_las_demas(self):
        union = set()
        for option in LOCATION_OPTIONS + (NO_APPROVED_LOCATION,):
            union |= self.projects_for(option)
        self.assertEqual(self.projects_for(ANY_PENDING), union)

    def test_el_proyecto_mixto_no_tiene_pendientes(self):
        """Ninguna de sus dos ubicaciones cae en un cajón, y tiene una
        aprobada: `any_pending` no puede recogerlo."""
        self.assertNotIn(self.mixto.pk, self.projects_for(ANY_PENDING))

    def test_las_ubicaciones_sin_proyecto_quedan_fuera(self):
        for option in LOCATION_OPTIONS + (ANY_PENDING,):
            with self.subTest(option=option):
                self.assertNotIn(self.huerfana, Location.objects.filter(
                    location_pending_q(option)))
