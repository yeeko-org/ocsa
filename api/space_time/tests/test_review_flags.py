"""Marcado editorial de ubicaciones (`space_time/review_flags.py`).

Lo que hay que proteger es lo que no se puede deshacer solo: que el
comentario no se duplique al repetir la corrida, que el estatus se mueva
únicamente desde «Aprobado», y que la reversa devuelva el estatus previo
sin llevarse el comentario que ya había escrito un editor.

La selección (`scan`) no entra aquí: vive en `far_pins.py` y necesita
cartografía; estos tests parten de entradas ya seleccionadas.
"""

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, TestCase

from project.models import Project
from space_time.models import Location
from space_time.review_flags import (
    APPROVED, FLAGGED, Entry, Flagger, Reverter, append_comment, signed,
    strip_comment)
from work_flux.models import StatusControl

DAY = date(2026, 8, 28)
HUMAN = "12/03/2026 - Gabriel: el punto es aproximado"
TEXT = "el pin está a 40.6 km del municipio capturado (Carichí); revisar."


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
        cls.approved = StatusControl.objects.create(
            name=APPROVED, group="location", public_name="Aprobado")
        cls.flagged = StatusControl.objects.create(
            name=FLAGGED, group="location",
            public_name="Aprobado (con observaciones)")
        cls.filled = StatusControl.objects.create(
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
