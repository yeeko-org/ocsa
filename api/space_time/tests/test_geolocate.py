"""Motor de geolocalización `space_time/geolocate.py` (docs `adr-0026`).

Corre sobre cartografía sintética —municipios cuadrados y localidades
inventadas en EPSG:6372—, así que no necesita los shapefiles del INEGI
descargados.
"""

from django.test import TestCase

from shapely import wkb as shapely_wkb
from shapely.geometry import Point, box

from space_time import geolocate
from space_time.models import (
    Locality, LocalityGeometry, Location, Municipality, MunicipalityGeometry,
    State, StateGeometry)


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
