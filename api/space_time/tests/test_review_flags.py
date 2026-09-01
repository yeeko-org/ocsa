"""Marcado editorial de ubicaciones (`space_time/review_flags.py`).

Lo que hay que proteger es lo que no se puede deshacer solo: que el
comentario no se duplique al repetir la corrida, que el estatus se mueva
únicamente desde «Aprobado», y que la reversa devuelva el estatus previo
sin llevarse el comentario que ya había escrito un editor.

La selección de pines contra el municipio (`far_pins.scan`) no entra
aquí: necesita la cartografía del INEGI y estos tests parten de entradas
ya seleccionadas. Las demás selecciones sí, porque corren sobre la
cartografía sintética.
"""

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, TestCase

from shapely import wkb as shapely_wkb

from project.models import Project
from space_time.far_pins import (
    locality_point, locality_polygon, municipality_polygon,
    municipality_simplification_m, scan as scan_pins,
    scan_localities as scan_locality_pins, state_polygon,
    state_simplification_m)
from space_time.models import (
    Location, Municipality, MunicipalityGeometry, StateGeometry)
from space_time.off_traces import (
    scan as scan_traces, scan_base_municipality as scan_base,
    scan_in_other_state, scan_localities as scan_trace_localities,
    scan_states as scan_off_states)
from space_time.review_flags import (
    APPROVED, FLAGGED, Entry, Flagger, Reverter, append_comment,
    base_off_crossed_text, far_locality_text, in_other_state_text,
    off_locality_text, off_state_text, off_trace_text, signed,
    state_mismatch_text, strip_comment)
from space_time.state_mismatch import scan as scan_states
from space_time.tests.test_geolocate import SyntheticCartography
from work_flux.test_helpers import make_status

DAY = date(2026, 8, 28)
HUMAN = "12/03/2026 - Gabriel: el punto es aproximado"
TEXT = "el pin está a 40.6 km del municipio capturado (Carichí); revisar."
OTHER_TEXT = "el estado capturado (Sonora) no es el del municipio."


class CommentTextTests(SimpleTestCase):
    """El formato y la reversa del texto, sin base de datos."""

    def test_la_firma_lleva_fecha_y_nombre(self):
        self.assertEqual(
            signed("texto", DAY), "28/08/2026 - Ricardo: texto")

    def test_el_comentario_vacio_no_arrastra_separador(self):
        self.assertEqual(append_comment(None, "nuevo"), "nuevo")

    def test_el_comentario_previo_se_conserva(self):
        self.assertEqual(
            append_comment(HUMAN, "nuevo"), f"{HUMAN}\n\nnuevo")

    def test_quitar_el_agregado_conserva_lo_humano(self):
        comments = append_comment(HUMAN, "nuevo")
        self.assertEqual(strip_comment(comments, "nuevo"), HUMAN)

    def test_quitar_el_unico_comentario_deja_nulo(self):
        self.assertIsNone(strip_comment("nuevo", "nuevo"))


class FlaggerTests(TestCase):
    """La regla de estatus, la idempotencia y la reversa, sobre la base."""

    @classmethod
    def setUpTestData(cls):
        cls.approved = make_status(
            name=APPROVED, group="location", public_name="Aprobado")
        cls.flagged = make_status(
            name=FLAGGED, group="location",
            public_name="Aprobado (con observaciones)")
        cls.filled = make_status(
            name="filled", group="location", public_name="Datos completos")
        cls.project = Project.objects.create(name="Proyecto de prueba")

    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.out = str(Path(self.directory.name) / "flags.csv")

    def location(self, status, comments=None):
        return Location.objects.create(
            project=self.project, status_location=status, comments=comments,
            latitude=19.0, longitude=-102.0)

    def flag(self, *locations, day=DAY, apply=True):
        """Corre el marcado sobre entradas dadas, sin pasar por `scan`."""
        flagger = Flagger(apply, self.out, day=day)
        entries = {}
        for location in locations:
            entry = Entry(location)
            entry.add("far_pin", TEXT)
            entries[location.pk] = entry
        for pk in sorted(entries):
            flagger.flag(entries[pk])
        if apply:
            Location.objects.bulk_update(
                flagger.pending, ["status_location", "comments"])
        flagger.write_csv()
        return flagger

    def test_aprobado_pasa_a_aprobado_con_observaciones(self):
        location = self.location(self.approved)
        self.flag(location)
        location.refresh_from_db()
        self.assertEqual(location.status_location_id, FLAGGED)
        self.assertEqual(location.comments, signed(TEXT, DAY))

    def test_otro_estatus_recibe_comentario_y_no_se_mueve(self):
        location = self.location(self.filled)
        self.flag(location)
        location.refresh_from_db()
        self.assertEqual(location.status_location_id, "filled")
        self.assertEqual(location.comments, signed(TEXT, DAY))

    def test_repetir_la_corrida_no_duplica_el_comentario(self):
        location = self.location(self.approved)
        self.flag(location)
        location.refresh_from_db()
        # Otro día: la firma cambia, pero el texto ya está y no se repite.
        second = self.flag(location, day=date(2026, 9, 1))
        location.refresh_from_db()
        self.assertEqual(location.comments.count(TEXT), 1)
        self.assertEqual(second.counts["far_pin"]["ya_marcada"], 1)

    def test_la_razon_ya_comentada_cuenta_aunque_otra_sea_nueva(self):
        """La cuenta va por razón: una entrada mixta suma en las dos."""
        location = self.location(
            self.approved, comments=signed(TEXT, DAY))
        flagger = Flagger(False, self.out, day=DAY)
        entry = Entry(location)
        entry.add("far_pin", TEXT)
        entry.add("state_mismatch", OTHER_TEXT)
        flagger.flag(entry)

        self.assertEqual(flagger.counts["far_pin"]["ya_marcada"], 1)
        self.assertEqual(flagger.counts["state_mismatch"]["ya_marcada"], 0)
        self.assertEqual(flagger.counts["state_mismatch"]["estatus"], 1)
        self.assertEqual(len(flagger.rows), 1)

    def test_la_reversa_restaura_estatus_y_quita_solo_lo_agregado(self):
        location = self.location(self.approved, comments=HUMAN)
        self.flag(location)
        Reverter(self.out).run()
        location.refresh_from_db()
        self.assertEqual(location.status_location_id, APPROVED)
        self.assertEqual(location.comments, HUMAN)

    def test_la_reversa_deja_nulo_el_comentario_que_no_existia(self):
        location = self.location(self.filled)
        self.flag(location)
        Reverter(self.out).run()
        location.refresh_from_db()
        self.assertEqual(location.status_location_id, "filled")
        self.assertIsNone(location.comments)


class OffTraceTests(SyntheticCartography, TestCase):
    """La selección de trazos fuera del municipio capturado.

    El corte es la intersección vacía y no el umbral de cruce: un trazo
    que apenas roza el municipio capturado ya lo justifica.
    """

    def setUp(self):
        super().setUp()
        # El polígono del municipio y su simplificación se cachean por
        # id, y los ids se reciclan entre tests, que hacen rollback.
        municipality_polygon.cache_clear()
        municipality_simplification_m.cache_clear()

    def trace(self, municipality, points):
        return Location.objects.create(
            type_location="line", state=self.state,
            municipality=municipality,
            geojson=self._feature("LineString", points))

    def test_el_trazo_en_otro_municipio_se_marca(self):
        location = self.trace(self.west, [(1.2, 0.5), (1.8, 0.5)])

        found, seen = scan_traces()

        self.assertEqual(seen, 1)
        self.assertEqual([off.location.pk for off in found], [location.pk])
        # El texto nombra el capturado y no enumera los atravesados,
        # que el editor ya ve en la ficha.
        text = off_trace_text(found[0])
        self.assertIn(self.west.name, text)
        self.assertNotIn(self.east.name, text)

    def test_el_trazo_que_apenas_roza_su_municipio_no_se_marca(self):
        # 10 m dentro del oeste: por debajo del umbral de cruce, así que
        # el motor no lo cuenta como atravesado, pero sí lo toca.
        self.trace(self.west, [(0.999, 0.5), (1.8, 0.5)])

        found, seen = scan_traces()

        self.assertEqual(seen, 1)
        self.assertEqual(found, [])

    def test_el_trazo_a_diez_metros_del_borde_no_se_marca(self):
        """La gracia es la simplificación de la capa (50 m en la
        cartografía sintética): por debajo de ella la separación es del
        dibujo y no de la captura."""
        self.trace(self.west, [(1.001, 0.5), (1.5, 0.5)])

        found, seen = scan_traces()

        self.assertEqual(seen, 1)
        self.assertEqual(found, [])


class BaseOffCrossedTests(SyntheticCartography, TestCase):
    """El municipio capturado que el trazo no atraviesa.

    A diferencia de `trace_off_municipality`, el corte es la medida del
    motor y no el contacto: el roce cuenta allá y no cuenta aquí.
    """

    def setUp(self):
        super().setUp()
        municipality_polygon.cache_clear()
        municipality_simplification_m.cache_clear()

    def trace(self, municipality, points):
        return Location.objects.create(
            type_location="line", state=self.state,
            municipality=municipality,
            geojson=self._feature("LineString", points))

    def test_el_roce_de_diez_metros_no_cuenta_como_atravesado(self):
        """Justo el caso que `trace_off_municipality` deja pasar: el
        trazo toca el oeste, pero el motor solo atraviesa el este."""
        location = self.trace(self.west, [(0.999, 0.5), (1.8, 0.5)])

        found, seen = scan_base()

        self.assertEqual(seen, 1)
        self.assertEqual([off.location.pk for off in found], [location.pk])
        self.assertIn(self.west.name, base_off_crossed_text(found[0]))

    def test_el_trazo_que_si_atraviesa_su_municipio_no_se_marca(self):
        self.trace(self.west, [(0.2, 0.5), (0.8, 0.5)])

        found, seen = scan_base()

        self.assertEqual(seen, 1)
        self.assertEqual(found, [])


class OffStateTests(SyntheticCartography, TestCase):
    """La selección de trazos fuera del estado capturado.

    Es la única razón que alcanza a un trazo sin municipio capturado.
    """

    def setUp(self):
        super().setUp()
        state_polygon.cache_clear()
        state_simplification_m.cache_clear()

    def trace(self, points):
        return Location.objects.create(
            type_location="line", state=self.state,
            geojson=self._feature("LineString", points))

    def test_el_trazo_fuera_del_estado_se_marca_sin_municipio(self):
        """A 2 km al este del polígono estatal, y sin municipio
        capturado: ninguna otra razón lo vería."""
        location = self.trace([(2.2, 0.5), (2.4, 0.5)])

        found, seen = scan_off_states()

        self.assertEqual(seen, 1)
        self.assertEqual([off.location.pk for off in found], [location.pk])
        self.assertEqual(found[0].distance, 2.0)
        text = off_state_text(found[0])
        self.assertIn("2.0 km", text)
        # El estado capturado se nombra; los calculados no, porque el
        # dashboard ya los muestra.
        self.assertIn(self.state.name, text)
        self.assertNotIn(self.other_state.name, text)

    def test_el_trazo_a_veinte_metros_del_borde_no_se_marca(self):
        """La gracia es la simplificación de la capa estatal (50 m)."""
        self.trace([(2.002, 0.5), (2.01, 0.5)])

        found, seen = scan_off_states()

        self.assertEqual(seen, 1)
        self.assertEqual(found, [])

    def test_el_trazo_dentro_de_su_estado_no_se_marca(self):
        self.trace([(0.2, 0.5), (1.8, 0.5)])

        found, seen = scan_off_states()

        self.assertEqual(seen, 1)
        self.assertEqual(found, [])


class OffLocalityTests(SyntheticCartography, TestCase):
    """La selección de trazos lejos de la localidad capturada.

    El corte es la distancia de 5 km y no el contacto, para que la marca
    diga lo mismo que el aviso que el editor ve al dibujar.
    """

    def setUp(self):
        super().setUp()
        # Ambas cachés van por id de localidad y los ids se reciclan
        # entre tests, que hacen rollback.
        locality_polygon.cache_clear()
        locality_point.cache_clear()

    def trace(self, locality, points):
        return Location.objects.create(
            type_location="line", state=self.state, locality=locality,
            geojson=self._feature("LineString", points))

    def test_el_trazo_lejos_de_su_localidad_se_marca(self):
        # 8 km al punto de catálogo de la única del oeste, que está en
        # (0.5, 0.5): sin contacto y fuera de la tolerancia.
        location = self.trace(self.only_one, [(1.3, 0.5), (1.5, 0.5)])

        found, seen = scan_trace_localities()

        self.assertEqual(seen["seen"], 1)
        self.assertEqual(seen["point"], 1)
        self.assertEqual([off.location.pk for off in found], [location.pk])
        self.assertEqual(found[0].measured_on, "point")
        text = off_locality_text(found[0])
        self.assertIn(self.only_one.name, text)
        self.assertIn("8.0 km", text)

    def test_el_trazo_a_tres_kilometros_no_se_marca(self):
        """Tampoco toca la localidad, pero cae dentro de la tolerancia."""
        self.trace(self.only_one, [(0.8, 0.5), (1.0, 0.5)])

        found, seen = scan_trace_localities()

        self.assertEqual(seen["seen"], 1)
        self.assertEqual(found, [])

    def test_la_localidad_amanzanada_se_mide_contra_su_poligono(self):
        """El trazo está a 1 km del borde de la mancha urbana y a 4 km de
        su punto de catálogo: con un umbral de 2 km solo el polígono lo
        salva."""
        self.trace(self.urban, [(1.9, 0.5), (2.0, 0.5)])

        found, seen = scan_trace_localities(2.0)

        self.assertEqual(seen["polygon"], 1)
        self.assertEqual(found, [])


class FarLocalityPinTests(SyntheticCartography, TestCase):
    """La selección de pines lejos de la localidad capturada."""

    def setUp(self):
        super().setUp()
        # Todas las cachés van por id y los ids se reciclan entre
        # tests, que hacen rollback.
        locality_polygon.cache_clear()
        locality_point.cache_clear()
        municipality_polygon.cache_clear()
        state_polygon.cache_clear()
        state_simplification_m.cache_clear()

    def pin(self, locality, fx, fy, **extra):
        latitude, longitude = self._latlon(fx, fy)
        return Location.objects.create(
            type_location="point", state=self.state, locality=locality,
            latitude=latitude, longitude=longitude, **extra)

    def test_el_pin_lejos_de_su_localidad_se_marca(self):
        """5.7 km al punto de catálogo de la única del oeste."""
        location = self.pin(self.only_one, 0.9, 0.9)

        found, seen = scan_locality_pins(2.0)

        self.assertEqual(seen["seen"], 1)
        self.assertEqual(seen["point"], 1)
        self.assertEqual([pin.location.pk for pin in found], [location.pk])
        self.assertEqual(found[0].measured_on, "point")
        self.assertIn(self.only_one.name, far_locality_text(found[0]))
        self.assertIn("5.7 km", far_locality_text(found[0]))

    def test_la_localidad_amanzanada_se_mide_contra_su_poligono(self):
        """El pin está a 1 km del borde de la mancha urbana y a 4 km de
        su punto de catálogo: medido por punto saldría marcado."""
        self.pin(self.urban, 1.9, 0.5)

        found, seen = scan_locality_pins(2.0)

        self.assertEqual(seen["polygon"], 1)
        self.assertEqual(found, [])

    def test_el_pin_aproximado_no_entra_al_universo(self):
        """Su coordenada señala el rumbo, no el sitio: medirle
        kilómetros a la localidad no dice nada. El mismo pin en otro
        estatus sí sale marcado."""
        self.pin(self.only_one, 0.9, 0.9,
                 status_location=self.approximate)

        found, seen = scan_locality_pins(2.0)

        self.assertEqual(seen["seen"], 0)
        self.assertEqual(found, [])

    def test_el_pin_aproximado_si_se_mide_contra_municipio_y_estado(self):
        """La exclusión es solo de la localidad: contra el municipio y
        contra el estado la imprecisión del rumbo no salva nada."""
        location = self.pin(
            self.only_one, 1.9, 0.9, municipality=self.west,
            status_location=self.approximate,
            project=Project.objects.create(name="Aproximado"))

        found, seen = scan_pins()

        self.assertEqual(seen, 1)
        self.assertEqual([pin.location.pk for pin in found], [location.pk])


class StateMismatchTests(SyntheticCartography, TestCase):
    """La selección de estados que no son los de su municipio."""

    def test_el_estado_ajeno_al_municipio_se_marca(self):
        location = Location.objects.create(
            type_location="point", state=self.other_state,
            municipality=self.west)
        Location.objects.create(
            type_location="point", state=self.state, municipality=self.west)

        found, seen = scan_states()

        self.assertEqual(seen, 2)
        self.assertEqual([row.location.pk for row in found], [location.pk])
        text = state_mismatch_text(found[0])
        self.assertIn(self.other_state.name, text)
        self.assertIn(self.west.name, text)
        self.assertIn(self.state.name, text)


class InOtherStateTests(SyntheticCartography, TestCase):
    """Trazos que desbordan a otro estado sin salirse del capturado.

    Es la forma del caso 4513: un polígono repartido en muchos
    municipios del estado capturado y uno solo del vecino. Su distancia
    al polígono estatal es cero, así que `trace_off_state` no lo ve.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Tercer municipio, ya en la entidad ajena y pegado al este: sin
        # él no hay frontera estatal que desbordar. Su estado necesita
        # polígono porque los candidatos salen del índice estatal.
        cls.foreign = Municipality.objects.create(
            inegi_code="003", complete_code="98-003",
            name="Municipio 003", std_name="municipio 003",
            state=cls.other_state)
        square = cls._box(2.0, 0.0, 3.0, 1.0)
        MunicipalityGeometry.objects.create(
            municipality=cls.foreign, wkb=shapely_wkb.dumps(square))
        StateGeometry.objects.create(
            state=cls.other_state, wkb=shapely_wkb.dumps(square))

    def setUp(self):
        super().setUp()
        state_polygon.cache_clear()
        state_simplification_m.cache_clear()

    def trace(self, points):
        return Location.objects.create(
            type_location="polygon", state=self.state,
            geojson=self._feature("Polygon", points))

    def test_el_trazo_que_desborda_al_estado_vecino_se_marca(self):
        """Ocupa casi todo el este y entra 20 ha al municipio ajeno: no
        se salió de su estado, pero sí atraviesa uno de otro."""
        location = self.trace(
            [(1.2, 0.2), (2.2, 0.2), (2.2, 0.8), (1.2, 0.8)])

        found, seen = scan_in_other_state()

        self.assertEqual(seen, 1)
        self.assertEqual([off.location.pk for off in found], [location.pk])
        # Lo que ninguna otra razón alcanza: contra su propio estado el
        # trazo está a cero.
        self.assertEqual(scan_off_states()[0], [])
        text = in_other_state_text(found[0])
        self.assertIn("un municipio de otro estado", text)
        self.assertIn(self.state.name, text)
        self.assertNotIn(self.other_state.name, text)
        self.assertNotIn(self.foreign.name, text)

    def test_el_trazo_que_se_queda_en_su_estado_no_se_marca(self):
        self.trace([(0.2, 0.2), (1.8, 0.2), (1.8, 0.8), (0.2, 0.8)])

        found, seen = scan_in_other_state()

        self.assertEqual(seen, 1)
        self.assertEqual(found, [])
