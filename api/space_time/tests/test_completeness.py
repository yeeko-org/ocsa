"""Filtros «Pendientes de ubicación» de `space_time/completeness.py`
(docs `task-69`).

Protegen que la lista de ubicaciones y la de proyectos respondan a la
misma pregunta, y que `any_pending` sea la unión exacta de las demás
opciones.
"""

from django.test import TestCase

from project.models import Project
from space_time.completeness import (
    ANY_PENDING, COMPLETE_UNAPPROVED, LOCATION_OPTIONS, NO_APPROVED_LOCATION,
    NO_GEOMETRY, NO_MUNICIPALITY, location_pending_q, project_pending_q)
from space_time.models import Location, Municipality, State
from work_flux.test_helpers import make_status


class PendingFiltersTests(TestCase):
    """Filtros «Pendientes de ubicación» (task-69, `completeness.py`).

    Dos invariantes: lo que se ve en la lista de ubicaciones y lo que se
    ve en la de proyectos responden a la misma pregunta, y
    `any_pending` es exactamente la unión de las demás opciones —no una
    aproximación que coincida con los datos de hoy.
    """

    @classmethod
    def setUpTestData(cls):
        cls.aprobado = make_status(
            name="aprobado", group="location", public_name="Aprobada",
            is_public=True)
        cls.inicial = make_status(
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
