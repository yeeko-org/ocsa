"""Dictámenes del backfill (`space_time/backfill_verdicts.py`).

Lo que hay que proteger es lo destructivo: que reescribir el comentario
no se lleve por delante lo que escribió un editor, que `details` no
acumule la misma referencia dos veces, que un homónimo vacíe la capa que
corresponde, y que el dictamen humano llegue antes que el motor y le
gane el campo.
"""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, TestCase

from space_time.backfill import (
    BACKUP_FIELDS, HUMAN_VERDICTS, apply_and_diff, snapshot)
from space_time.backfill_verdicts import (
    VerdictApplier, append_detail, load_verdicts, rewrite_comments)
from space_time.models import Location
from space_time.tests.test_geolocate import SyntheticCartography

FRAGMENT_FIELDS = [
    "location_id", "template", "legacy_value", "match_level",
    "candidate_id", "verdict", "fragment_verbatim"]
LAYER_FIELDS = [
    "location_id", "state_proposed", "state_id", "municipality_proposed",
    "municipality_id", "locality_proposed", "locality_id", "confidence"]


def write_csv(directory: Path, name: str, fields: list,
              rows: list) -> str:
    path = directory / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


class RewriteCommentsTests(SimpleTestCase):
    """La reescritura del bloque `YEEKO:`, sin base de datos."""

    HUMAN = "12/03/2026 - Gabriel: el punto es aproximado"

    def test_conserva_el_texto_humano_al_quitar_el_ultimo_fragmento(self):
        comments = (
            "YEEKO: Municipio no encontrado: Cuajimalpa\n\n" + self.HUMAN)
        rewritten = rewrite_comments(
            comments, {"Municipio no encontrado: Cuajimalpa"})
        self.assertEqual(rewritten, self.HUMAN)

    def test_conserva_el_texto_humano_con_un_solo_salto(self):
        comments = "YEEKO: Localidad no encontrada: Polanco\n" + self.HUMAN
        rewritten = rewrite_comments(
            comments, {"Localidad no encontrada: Polanco"})
        self.assertEqual(rewritten, self.HUMAN)

    def test_sin_fragmentos_ni_texto_humano_el_comentario_queda_nulo(self):
        rewritten = rewrite_comments(
            "YEEKO: Localidad no encontrada: Polanco",
            {"Localidad no encontrada: Polanco"})
        self.assertIsNone(rewritten)

    def test_los_fragmentos_que_nadie_resolvio_siguen_en_la_linea(self):
        comments = ("YEEKO: Municipio no encontrado: Cuajimalpa; "
                    "Localidad no encontrada: El Contadero\n" + self.HUMAN)
        rewritten = rewrite_comments(
            comments, {"Municipio no encontrado: Cuajimalpa"})
        self.assertEqual(
            rewritten,
            "YEEKO: Localidad no encontrada: El Contadero\n" + self.HUMAN)

    def test_append_detail_respeta_lo_que_ya_habia(self):
        self.assertEqual(
            append_detail("Sobre la presa", "Polanco"),
            "Sobre la presa\nReferencia legacy: Polanco")
        self.assertEqual(
            append_detail(None, "Polanco"), "Referencia legacy: Polanco")


class ApplyVerdictsTests(SyntheticCartography, TestCase):
    """Los dictámenes sobre la cartografía sintética del motor."""

    def setUp(self):
        super().setUp()
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)

    def applier(self, *paths) -> VerdictApplier:
        return VerdictApplier(load_verdicts(paths))

    def location(self, **kwargs) -> Location:
        return Location.objects.create(**kwargs)

    def test_a_details_no_repite_lo_que_details_ya_dice(self):
        """La comparación es normalizada: «Polanco» ya está dentro de
        «Colonia Polanco, tercera sección»."""
        location = self.location(
            type_location="point",
            comments="YEEKO: Localidad no encontrada: Polanco",
            details="Colonia Polanco, tercera sección")
        source = write_csv(self.path, "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "localidad",
            "legacy_value": "Polanco", "match_level": "sin_match",
            "candidate_id": "", "verdict": "a_details",
            "fragment_verbatim": "Localidad no encontrada: Polanco"}])
        applier = self.applier(source)
        applier.apply(location)
        self.assertEqual(location.details, "Colonia Polanco, tercera sección")
        self.assertIsNone(location.comments)
        counts = applier.counts["v.csv"]
        self.assertEqual(counts["details_duplicado"], 1)
        self.assertEqual(counts["fragmentos_borrados"], 1)

    def test_a_details_agrega_la_referencia_cuando_no_estaba(self):
        location = self.location(
            type_location="point",
            comments="YEEKO: Localidad no encontrada: Wirikuta",
            details="Sierra de Catorce")
        source = write_csv(self.path, "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "localidad",
            "legacy_value": "Wirikuta", "match_level": "sin_match",
            "candidate_id": "", "verdict": "a_details",
            "fragment_verbatim": "Localidad no encontrada: Wirikuta"}])
        applier = self.applier(source)
        applier.apply(location)
        self.assertEqual(
            location.details,
            "Sierra de Catorce\nReferencia legacy: Wirikuta")
        self.assertEqual(applier.counts["v.csv"]["details_agregado"], 1)

    def test_vaciar_borra_la_capa_que_quedo_ambigua(self):
        """El legado llenó la localidad con el primero de dos homónimos:
        el municipio no se toca, solo la capa del fragmento."""
        location = self.location(
            type_location="point", municipality=self.west,
            locality=self.only_one,
            comments=("YEEKO: Se encontraron 2 localidades con el mismo "
                      "nombreSan Isidro"))
        source = write_csv(self.path, "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "homonimo",
            "legacy_value": "San Isidro", "match_level": "homonimo",
            "candidate_id": "138592|138704", "verdict": "vaciar",
            "fragment_verbatim": ("Se encontraron 2 localidades con el "
                                  "mismo nombreSan Isidro")}])
        applier = self.applier(source)
        applier.apply(location)
        self.assertIsNone(location.locality_id)
        self.assertEqual(location.municipality_id, self.west.pk)
        self.assertIsNone(location.comments)
        self.assertEqual(applier.counts["v.csv"]["vaciar"], 1)

    def test_llenar_no_pisa_un_campo_ya_capturado_ni_borra_el_fragmento(self):
        """Si lo capturado contradice al dictamen, el comentario es la
        única constancia del desacuerdo y se queda."""
        location = self.location(
            type_location="point", state=self.state, municipality=self.west,
            comments="YEEKO: Municipio no encontrado: Otro")
        source = write_csv(self.path, "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "municipio",
            "legacy_value": "Otro", "match_level": "fuzzy",
            "candidate_id": self.east.pk, "verdict": "llenar",
            "fragment_verbatim": "Municipio no encontrado: Otro"}])
        applier = self.applier(source)
        applier.apply(location)
        self.assertEqual(location.municipality_id, self.west.pk)
        self.assertEqual(
            location.comments, "YEEKO: Municipio no encontrado: Otro")
        self.assertEqual(applier.counts["v.csv"]["llenar_en_conflicto"], 1)

    def test_el_ultimo_csv_gana_sobre_el_mismo_fragmento(self):
        location = self.location(
            type_location="point", state=self.state,
            comments="YEEKO: Municipio no encontrado: Bocoyvo")
        row = {
            "location_id": location.pk, "template": "municipio",
            "legacy_value": "Bocoyvo", "match_level": "sin_match",
            "candidate_id": "", "verdict": "sin_resolver",
            "fragment_verbatim": "Municipio no encontrado: Bocoyvo"}
        automatic = write_csv(self.path, "auto.csv", FRAGMENT_FIELDS, [row])
        manual = write_csv(self.path, "manual.csv", FRAGMENT_FIELDS, [
            dict(row, verdict="llenar", candidate_id=self.east.pk)])
        applier = self.applier(automatic, manual)
        applier.apply(location)
        self.assertEqual(location.municipality_id, self.east.pk)
        self.assertIsNone(location.comments)
        self.assertNotIn("auto.csv", applier.counts)

    def test_el_csv_de_estados_llena_las_capas_que_resolvio(self):
        """Trae estado y municipio pero no localidad: ese fragmento se
        queda esperando."""
        location = self.location(
            type_location="point",
            comments=("YEEKO: Estado no encontrado: Sintetica; "
                      "Municipio no encontrado: Oeste; "
                      "Localidad no encontrada: Quién sabe"))
        source = write_csv(self.path, "estados.csv", LAYER_FIELDS, [{
            "location_id": location.pk,
            "state_proposed": self.state.name, "state_id": self.state.pk,
            "municipality_proposed": self.west.name,
            "municipality_id": self.west.pk,
            "locality_proposed": "", "locality_id": "",
            "confidence": "alta"}])
        applier = self.applier(source)
        applier.apply(location)
        self.assertEqual(location.state_id, self.state.pk)
        self.assertEqual(location.municipality_id, self.west.pk)
        self.assertIsNone(location.locality_id)
        self.assertEqual(
            location.comments,
            "YEEKO: Localidad no encontrada: Quién sabe")


class VerdictBeforeEngineTests(SyntheticCartography, TestCase):
    """El orden dentro de `apply_and_diff`: dictamen y luego motor."""

    def test_el_dictamen_gana_el_campo_que_el_motor_habria_llenado(self):
        """El punto cae en el oeste y el motor llenaría ese municipio;
        el dictamen dice este, y como el motor solo llena lo vacío, el
        que corre primero es el que se queda."""
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        latitude, longitude = self._latlon(0.5, 0.5)
        location = Location.objects.create(
            type_location="point", latitude=latitude, longitude=longitude,
            comments="YEEKO: Municipio no encontrado: Vecino")
        source = write_csv(Path(directory.name), "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "municipio",
            "legacy_value": "Vecino", "match_level": "fuzzy",
            "candidate_id": self.east.pk, "verdict": "llenar",
            "fragment_verbatim": "Municipio no encontrado: Vecino"}])
        applier = VerdictApplier(load_verdicts([source]))
        filled, before, after, sources = apply_and_diff(location, applier)

        self.assertEqual(location.municipality_id, self.east.pk)
        self.assertEqual(sources["municipality_id"], "v.csv")
        self.assertIn("comments", filled)
        self.assertEqual(after["comments"], None)
        # El motor sí corrió: el estado lo arrastró la localidad que él
        # resolvió, y esa escritura no tiene origen de dictamen.
        self.assertIn("locality", filled)
        self.assertNotIn("locality_id", sources)
        self.assertIsNotNone(before["comments"])

    def test_el_veredicto_humano_gana_sobre_el_dictamen_del_csv(self):
        """`HUMAN_VERDICTS` es el último recurso: veta el campo aunque
        el CSV traiga un `llenar` con candidato."""
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        vetoed_id = next(
            key for key, fields in HUMAN_VERDICTS.items()
            if "locality" in fields)
        latitude, longitude = self._latlon(0.5, 0.5)
        location = Location.objects.create(
            id=vetoed_id, type_location="point",
            latitude=latitude, longitude=longitude,
            comments="YEEKO: Localidad no encontrada: Inventada")
        source = write_csv(Path(directory.name), "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "localidad",
            "legacy_value": "Inventada", "match_level": "fuzzy",
            "candidate_id": self.only_one.pk, "verdict": "llenar",
            "fragment_verbatim": "Localidad no encontrada: Inventada"}])
        applier = VerdictApplier(load_verdicts([source]))
        filled, _before, after, _sources = apply_and_diff(location, applier)

        self.assertIsNone(location.locality_id)
        self.assertIsNone(after["locality_id"])
        self.assertNotIn("locality", filled)
        # El comentario sí se limpia: lo vetado es el campo, no la
        # constancia de que el legado no supo resolverlo.
        self.assertIn("comments", filled)


class BackupRoundTripTests(SyntheticCartography, TestCase):
    """`comments` y `details` viajan en el respaldo como todo lo demás."""

    def test_restaurar_el_antes_devuelve_el_comentario_intacto(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        original = "YEEKO: Localidad no encontrada: Polanco\n\nnota humana"
        location = Location.objects.create(
            type_location="point", comments=original, details="algo")
        source = write_csv(Path(directory.name), "v.csv", FRAGMENT_FIELDS, [{
            "location_id": location.pk, "template": "localidad",
            "legacy_value": "Polanco", "match_level": "sin_match",
            "candidate_id": "", "verdict": "a_details",
            "fragment_verbatim": "Localidad no encontrada: Polanco"}])
        applier = VerdictApplier(load_verdicts([source]))
        _filled, before, after, _sources = apply_and_diff(location, applier)

        self.assertEqual(after["comments"], "nota humana")
        self.assertEqual(after["details"], "algo\nReferencia legacy: Polanco")
        for name in BACKUP_FIELDS:
            setattr(location, name, before[name])
        restored = snapshot(location, [])
        self.assertEqual(restored["comments"], original)
        self.assertEqual(restored["details"], "algo")
