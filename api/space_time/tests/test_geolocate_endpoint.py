"""Endpoint `/api/location/geolocate/` sobre cartografía sintética.

Prueba el contrato que consume `useGeolocate` en el front —qué sugiere
el servidor para un punto (`GET`) y para un trazo (`POST`), y qué se
niega a sugerir—, no el motor: eso es `test_geolocate.py`, de donde se
reusa `SyntheticCartography`.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from shapely import wkb as shapely_wkb
from shapely.geometry import box

from profile_auth.models import User
from space_time.models import (
    Municipality, MunicipalityGeometry, StateGeometry)
from space_time.tests.test_geolocate import SyntheticCartography


class GeolocatePostTests(SyntheticCartography, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Tercer municipio, ya en la entidad ajena y pegado al este: es
        # lo único que permite un trazo interestatal.
        cls.foreign = Municipality.objects.create(
            inegi_code="003", complete_code="98-003",
            name="Municipio 003", std_name="municipio 003",
            state=cls.other_state)
        left = cls.x0 + 2 * cls.SIDE
        square = box(left, cls.y0, left + cls.SIDE, cls.y0 + cls.SIDE)
        MunicipalityGeometry.objects.create(
            municipality=cls.foreign, wkb=shapely_wkb.dumps(square))
        # Los candidatos salen del índice estatal: sin polígono de la
        # entidad ajena, su municipio nunca entraría a la comparación.
        StateGeometry.objects.create(
            state=cls.other_state, wkb=shapely_wkb.dumps(square))
        # Dos localidades sueltas sobre el eje del municipio ajeno, a 3 y
        # a 8 km del trazo de prueba: es lo que separa la tolerancia de
        # 5 km del aviso.
        cls.near = cls._locality(cls.foreign, "0001", 2.4, 0.5)
        cls.far = cls._locality(cls.foreign, "0002", 2.9, 0.5)
        cls.user = User.objects.create_user(
            username="capturista", password="x", full_editor=True)

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _post(self, feature, state=None):
        return self.client.post(
            reverse("location-geolocate"),
            {"geojson": feature, "state": state}, format="json")

    def test_el_poligono_de_un_municipio_sugiere_estado_y_municipio(self):
        feature = self._feature(
            "Polygon", [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)])
        data = self._post(feature).data
        self.assertEqual(data["state"]["id"], self.state.pk)
        self.assertEqual(data["municipality"]["id"], self.west.pk)
        self.assertEqual(
            data["municipalities"],
            [{"id": self.west.pk, "name": self.west.name,
              "state": self.state.pk}])
        self.assertIsNotNone(data["centroid"])

    def test_el_trazo_entre_dos_estados_no_sugiere_estado(self):
        """Cruza el este y el municipio de la entidad ajena, 8 km y 4 km:
        sin municipio base no hay estado que heredar, y los atravesados
        salen de mayor a menor medida."""
        feature = self._feature("LineString", [(1.2, 0.5), (2.4, 0.5)])
        data = self._post(feature).data
        self.assertIsNone(data["state"])
        self.assertIsNone(data["municipality"])
        self.assertEqual(
            [item["id"] for item in data["municipalities"]],
            [self.east.pk, self.foreign.pk])

    def test_las_localidades_llegan_hasta_cinco_kilometros_del_trazo(self):
        """Ninguna de las dos toca el trazo: lo que decide es la
        distancia, y con ella entra la de 3 km y queda fuera la de 8."""
        feature = self._feature("LineString", [(2.05, 0.5), (2.1, 0.5)])
        data = self._post(feature).data
        self.assertEqual(
            [item["id"] for item in data["localities"]], [self.near.pk])

    def test_cada_candidata_del_trazo_trae_distancia_y_punto(self):
        """El contrato que dibuja el front: además de id, nombre y
        municipio, la distancia con la que decide el aviso y el punto
        con el que la pinta."""
        feature = self._feature("LineString", [(2.05, 0.5), (2.1, 0.5)])
        candidate = self._post(feature).data["localities"][0]
        self.assertEqual(
            set(candidate),
            {"id", "name", "municipality", "distance_km", "point"})
        self.assertEqual(candidate["municipality"], self.foreign.pk)
        self.assertAlmostEqual(candidate["distance_km"], 3.0, places=2)
        latitude, longitude = self._latlon(2.4, 0.5)
        self.assertAlmostEqual(candidate["point"][0], longitude, places=4)
        self.assertAlmostEqual(candidate["point"][1], latitude, places=4)

    def test_acepta_la_geometria_pelona_igual_que_el_feature(self):
        feature = self._feature("LineString", [(0.2, 0.5), (0.8, 0.5)])
        wrapped = self._post(feature).data
        bare = self._post(feature["geometry"]).data
        self.assertEqual(wrapped, bare)
        self.assertEqual(wrapped["municipality"]["id"], self.west.pk)


class GeolocateGetTests(SyntheticCartography, TestCase):
    """El `GET` de un punto: lo mismo que el motor, más las candidatas.

    Su universo es el del motor —las localidades del municipio
    resuelto—, medidas contra el polígono de la amanzanada y contra el
    punto de catálogo de la que no lo tiene.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(
            username="capturista_get", password="x", full_editor=True)

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def _get(self, fx, fy):
        latitude, longitude = self._latlon(fx, fy)
        return self.client.get(
            reverse("location-geolocate"),
            {"lat": latitude, "lon": longitude, "state": self.state.pk}).data

    def test_las_candidatas_salen_ordenadas_por_distancia(self):
        """El pin cae dentro de la mancha urbana (0 km); las otras dos
        del este quedan a 0.7 y a 4.7 km, todas dentro de los 5 km."""
        data = self._get(1.25, 0.45)
        self.assertEqual(data["locality"]["id"], self.urban.pk)
        distances = [item["distance_km"] for item in data["localities"]]
        self.assertEqual(distances, sorted(distances))
        self.assertEqual(data["localities"][0]["id"], self.urban.pk)
        self.assertEqual(data["localities"][0]["distance_km"], 0.0)
        self.assertAlmostEqual(
            data["localities"][1]["distance_km"], 0.707, places=2)
        self.assertIsNotNone(data["localities"][0]["point"])

    def test_las_candidatas_se_quedan_dentro_de_los_cinco_kilometros(self):
        """En la esquina noroeste del oeste la única vigente queda a
        6.8 km: no hay candidata que ofrecer, ni localidad que sugerir."""
        data = self._get(0.02, 0.98)
        self.assertEqual(data["municipality"]["id"], self.west.pk)
        self.assertIsNone(data["locality"])
        self.assertEqual(data["localities"], [])
