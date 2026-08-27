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
from shapely import wkb as shapely_wkb
from shapely.geometry import Point, box

from space_time import geolocate
from space_time.models import (
    Locality, LocalityGeometry, Location, Municipality, MunicipalityGeometry,
    State, StateGeometry)
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


class GeolocateTests(TestCase):
    """El motor de `space_time.geolocate` sobre cartografía sintética.

    Dos municipios cuadrados de 10 km, pegados por su frontera este-oeste,
    guardados como `MunicipalityGeometry` en EPSG:6372 igual que los del
    INEGI. No se toca ningún shapefile: la suite corre sin los insumos
    descargados.
    """

    SIDE = 10_000.0

    @classmethod
    def setUpTestData(cls):
        cls.state = State.objects.create(inegi_code="99", name="Sintética")
        cls.other_state = State.objects.create(
            inegi_code="98", name="Ajena")
        origin = geolocate.point_in_meters(19.0, -102.0)
        cls.x0, cls.y0 = origin.x, origin.y
        cls.west = cls._municipality("001", 0)
        cls.east = cls._municipality("002", 1)
        StateGeometry.objects.create(
            state=cls.state,
            wkb=shapely_wkb.dumps(box(
                cls.x0, cls.y0, cls.x0 + 2 * cls.SIDE, cls.y0 + cls.SIDE)))
        # Una sola localidad en el municipio oeste y dos en el este: es lo
        # que separa «hay localidad» de «hay varias, no elijo».
        cls.only_one = cls._locality(cls.west, "0001", 0.5, 0.5)
        cls._locality(cls.east, "0001", 1.3, 0.4)
        cls._locality(cls.east, "0002", 1.7, 0.6)
        # Mancha urbana del este: su punto de catálogo está en el centro,
        # lejos de la esquina, y ahí es donde el vecino más cercano falla.
        cls.urban = cls._locality(cls.east, "0003", 1.5, 0.5)
        LocalityGeometry.objects.create(
            locality=cls.urban,
            wkb=shapely_wkb.dumps(cls._box(1.2, 0.2, 1.8, 0.8)))
        cls.retired = cls._locality(
            cls.west, "0009", 0.7, 0.7, is_current=False)

    @classmethod
    def _municipality(cls, code: str, column: int):
        municipality = Municipality.objects.create(
            inegi_code=code, complete_code=f"99-{code}",
            name=f"Municipio {code}", std_name=f"municipio {code}",
            state=cls.state)
        left = cls.x0 + column * cls.SIDE
        MunicipalityGeometry.objects.create(
            municipality=municipality,
            wkb=shapely_wkb.dumps(box(
                left, cls.y0, left + cls.SIDE, cls.y0 + cls.SIDE)))
        return municipality

    @classmethod
    def _locality(cls, municipality, code: str, fx: float, fy: float,
                  is_current: bool = True):
        latitude, longitude = cls._latlon(fx, fy)
        return Locality.objects.create(
            inegi_code=code,
            complete_code=f"{municipality.complete_code}-{code}",
            name=f"Localidad {municipality.inegi_code}-{code}",
            municipality=municipality, latitude=latitude, longitude=longitude,
            is_current=is_current)

    @classmethod
    def _box(cls, fx0: float, fy0: float, fx1: float, fy1: float):
        """Caja en metros, en lados del municipio desde el origen."""
        return box(cls.x0 + fx0 * cls.SIDE, cls.y0 + fy0 * cls.SIDE,
                   cls.x0 + fx1 * cls.SIDE, cls.y0 + fy1 * cls.SIDE)

    @classmethod
    def _latlon(cls, fx: float, fy: float) -> tuple:
        """Grados del punto que está a `(fx, fy)` lados del origen."""
        point = geolocate.to_latlon(
            Point(cls.x0 + fx * cls.SIDE, cls.y0 + fy * cls.SIDE))
        return point.y, point.x

    def setUp(self):
        # Los índices se cachean por proceso: cada test parte de cero.
        geolocate.clear_indexes()

    def _feature(self, geometry_type: str, points: list) -> dict:
        coordinates = [list(reversed(self._latlon(*pair))) for pair in points]
        if geometry_type == "Polygon":
            coordinates = [coordinates + [coordinates[0]]]
        return {"type": "Feature", "properties": {},
                "geometry": {"type": geometry_type,
                             "coordinates": coordinates}}

    # --- puntos ---

    def test_el_punto_cae_en_su_municipio_y_su_localidad(self):
        latitude, longitude = self._latlon(0.5, 0.5)
        resolution = geolocate.resolve_point(
            latitude, longitude, self.state.pk)
        self.assertEqual(resolution.municipality, self.west)
        self.assertEqual(resolution.state, self.state)
        self.assertEqual(resolution.locality, self.only_one)

    def test_el_estado_equivocado_no_impide_resolver(self):
        """El estado capturado se prueba primero, pero si el punto no cae
        ahí se resuelve por polígono en vez de devolver vacío."""
        latitude, longitude = self._latlon(1.5, 0.5)
        resolution = geolocate.resolve_point(
            latitude, longitude, self.other_state.pk)
        self.assertEqual(resolution.municipality, self.east)
        self.assertEqual(resolution.state, self.state)

    def test_el_punto_dentro_de_la_mancha_urbana_gana_al_vecino(self):
        """En (1.25, 0.45) el punto de la localidad rural 0001 está más
        cerca que el centro de la mancha urbana, pero el polígono manda."""
        latitude, longitude = self._latlon(1.25, 0.45)
        resolution = geolocate.resolve_point(
            latitude, longitude, self.state.pk)
        self.assertEqual(resolution.locality, self.urban)

    def test_el_punto_fuera_de_todo_poligono_cae_en_el_mas_cercano(self):
        latitude, longitude = self._latlon(1.9, 0.9)
        resolution = geolocate.resolve_point(
            latitude, longitude, self.state.pk)
        self.assertEqual(resolution.locality.inegi_code, "0002")

    def test_la_localidad_retirada_nunca_se_elige(self):
        """El punto cae encima de la retirada; la vigente está a 2.8 km."""
        latitude, longitude = self._latlon(0.7, 0.7)
        resolution = geolocate.resolve_point(
            latitude, longitude, self.state.pk)
        self.assertEqual(resolution.locality, self.only_one)

    def test_el_punto_fuera_de_toda_cartografia_queda_vacio(self):
        resolution = geolocate.resolve_point(19.0, -60.0)
        self.assertIsNone(resolution.state)
        self.assertIsNone(resolution.municipality)
        self.assertIsNone(resolution.locality)

    # --- trazos ---

    def test_la_linea_que_cruza_dos_municipios_no_llena_el_base(self):
        feature = self._feature("LineString", [(0.5, 0.5), (1.5, 0.5)])
        resolution = geolocate.resolve_geometry(feature)
        crossed = {municipality for municipality, _ in
                   resolution.municipalities}
        self.assertEqual(crossed, {self.west, self.east})
        self.assertIsNone(resolution.single_municipality)

    def test_el_roce_menor_al_umbral_no_cuenta_como_cruce(self):
        """La línea entra 30 m al municipio este: por debajo de los 50 m."""
        feature = self._feature(
            "LineString", [(0.5, 0.5), (1.003, 0.5)])
        resolution = geolocate.resolve_geometry(feature)
        crossed = [municipality for municipality, _ in
                   resolution.municipalities]
        self.assertEqual(crossed, [self.west])
        self.assertEqual(resolution.single_municipality, self.west)

    def test_el_centroide_de_la_linea_cae_sobre_ella(self):
        feature = self._feature("LineString", [(0.2, 0.5), (0.8, 0.5)])
        resolution = geolocate.resolve_geometry(feature)
        expected = self._latlon(0.5, 0.5)
        self.assertAlmostEqual(resolution.centroid[0], expected[0], places=3)
        self.assertAlmostEqual(resolution.centroid[1], expected[1], places=3)

    def test_el_poligono_con_una_localidad_la_asigna(self):
        feature = self._feature(
            "Polygon", [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)])
        resolution = geolocate.resolve_geometry(feature)
        self.assertEqual(resolution.nearby_localities, 1)
        self.assertEqual(resolution.locality, self.only_one)

    def test_el_trazo_hereda_el_estado_de_su_municipio_base(self):
        """El trazo nunca resuelve estado por polígono, pero el municipio
        base que sí resolvió arrastra el suyo."""
        feature = self._feature("LineString", [(0.5, 0.5), (0.8, 0.5)])
        resolution = geolocate.resolve_geometry(feature)
        self.assertIsNone(getattr(resolution, "state", None))
        location = Location.objects.create(
            type_location="line", geojson=feature)
        filled = geolocate.apply_geolocation(location)
        self.assertEqual(location.municipality, self.west)
        self.assertIn("state", filled)
        self.assertEqual(location.state, self.state)

    def test_el_trazo_sin_municipio_base_se_queda_sin_estado(self):
        """Atraviesa dos municipios: sin municipio base no hay de dónde
        heredar el estado, y el índice estatal no se consulta."""
        feature = self._feature("LineString", [(0.5, 0.5), (1.5, 0.5)])
        location = Location.objects.create(
            type_location="line", geojson=feature)
        filled = geolocate.apply_geolocation(location)
        self.assertIsNone(location.municipality)
        self.assertNotIn("state", filled)
        self.assertIsNone(location.state)

    def test_el_poligono_urbano_que_corta_el_trazo_cuenta_como_tocado(self):
        """La línea entra a la mancha urbana pero pasa a más de 500 m de
        los puntos de catálogo de las otras dos localidades del este."""
        feature = self._feature("LineString", [(1.25, 0.25), (1.75, 0.25)])
        resolution = geolocate.resolve_geometry(feature)
        self.assertEqual(resolution.nearby_localities, 1)
        self.assertEqual(resolution.locality, self.urban)

    def test_el_poligono_que_solo_colinda_no_atraviesa_al_vecino(self):
        """Comparte 1 km de frontera con el este sin entrar: la pieza es
        una línea de borde, y medirla por longitud lo daría por cruzado.

        Se mide contra `_crossing_measure` y no contra el trazo del
        editor porque el borde exacto solo existe entre polígonos que
        comparten vértices; el viaje a grados y de vuelta del geojson
        mueve el vértice y convierte la línea en una astilla.
        """
        drawn = self._box(0.9, 0.2, 1.0, 0.3)
        east = self._box(1.0, 0.0, 2.0, 1.0)
        self.assertIsNone(geolocate._crossing_measure(drawn, east))
        self.assertEqual(
            geolocate._crossing_measure(drawn, self._box(0.0, 0.0, 1.0, 1.0)),
            drawn.area)

    def test_el_poligono_pegado_a_la_frontera_llena_su_municipio(self):
        feature = self._feature(
            "Polygon", [(0.9, 0.2), (1.0, 0.2), (1.0, 0.3), (0.9, 0.3)])
        location = Location.objects.create(
            type_location="polygon", geojson=feature)
        geolocate.apply_geolocation(location)
        self.assertEqual(location.municipality, self.west)
        self.assertEqual(list(location.municipalities.all()), [self.west])

    def test_el_poligono_con_varias_localidades_deja_la_localidad_vacia(self):
        """Las tres del este: dos por su punto y la urbana por su polígono."""
        feature = self._feature(
            "Polygon", [(1.1, 0.2), (1.9, 0.2), (1.9, 0.8), (1.1, 0.8)])
        resolution = geolocate.resolve_geometry(feature)
        self.assertEqual(resolution.nearby_localities, 3)
        self.assertIsNone(resolution.locality)

    # --- aplicación ---

    def test_solo_llena_lo_vacio(self):
        latitude, longitude = self._latlon(0.5, 0.5)
        location = Location.objects.create(
            type_location="point", latitude=latitude, longitude=longitude,
            municipality=self.east)
        filled = geolocate.apply_geolocation(location)
        self.assertNotIn("municipality", filled)
        self.assertEqual(location.municipality, self.east)
        self.assertIn("state", filled)
        self.assertEqual(location.state, self.state)

    def test_el_punto_se_queda_con_su_municipio_en_el_m2m(self):
        latitude, longitude = self._latlon(0.5, 0.5)
        location = Location.objects.create(
            type_location="point", latitude=latitude, longitude=longitude)
        geolocate.apply_geolocation(location)
        location.save()
        self.assertEqual(list(location.municipalities.all()), [self.west])
        self.assertIsNone(location.nearby_localities)

    def test_el_trazo_persiste_municipios_centroide_y_conteo(self):
        feature = self._feature("LineString", [(0.5, 0.5), (1.5, 0.5)])
        location = Location.objects.create(
            type_location="line", geojson=feature)
        filled = geolocate.apply_geolocation(location)
        self.assertIn("latitude", filled)
        self.assertIsNotNone(location.latitude)
        self.assertEqual(
            set(location.municipalities.all()), {self.west, self.east})
        self.assertIsNone(location.municipality)
        self.assertIsNone(location.state)
