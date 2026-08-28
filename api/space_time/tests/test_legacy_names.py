"""Regla de coincidencia de los topónimos legados
(`space_time/legacy_names.py`).

Se prueba la función pura contra listas de candidatos armadas a mano: lo
que hay que proteger es el criterio —qué cuenta como exacto, dónde está
el umbral difuso, cuándo vale la contención y qué manda cuando el valor
huele a colonia—. De la consulta al catálogo solo se prueba a quién
deja fuera, que es donde puede desalinearse del motor.
"""

from django.test import SimpleTestCase, TestCase

from actor.migrate.common import text_normalizer
from space_time.legacy_names import (
    CONTAINED, EMPTY, EXACT, FILL, FUZZY, HOMONYM, NO_MATCH, NO_SCOPE,
    TEMPLATE_LOCALITY, TEMPLATE_MUNICIPALITY, TO_DETAILS, Candidate,
    CandidateIndex, match_legacy_name, verdict_for)
from space_time.tests.test_geolocate import SyntheticCartography


def candidates(*names) -> list[Candidate]:
    return [
        Candidate(i, name, text_normalizer(name))
        for i, name in enumerate(names, start=1)]


class MatchLegacyNameTests(SimpleTestCase):

    def test_exact_ignores_accents_and_spacing(self):
        rows = candidates("Juchitán de Zaragoza", "Ixtaltepec")
        match = match_legacy_name("JUCHITAN DE ZARAGOZA", rows)
        self.assertEqual(match.level, EXACT)
        self.assertEqual(match.candidate.name, "Juchitán de Zaragoza")
        self.assertEqual(match.score, 100.0)

    def test_fuzzy_boundary(self):
        """87.5 pasa, 82.4 no: el umbral de `fuzz.ratio` es 87."""
        rows = candidates("Amatitlán")
        self.assertEqual(match_legacy_name("Amatlán", rows).level, FUZZY)

        rows = candidates("Cuautitlán")
        below = match_legacy_name("Cuautla", rows)
        self.assertEqual(below.level, NO_MATCH)
        # El mejor candidato viaja igual, como material de revisión.
        self.assertEqual(below.candidate.name, "Cuautitlán")

    def test_containment_needs_to_be_unique(self):
        rows = candidates("Cuajimalpa de Morelos", "Tlalpan")
        match = match_legacy_name("Cuajimalpa", rows)
        self.assertEqual(match.level, CONTAINED)
        self.assertEqual(match.candidate.name, "Cuajimalpa de Morelos")

        ambiguous = candidates("Ixtapan de la Sal", "Ixtapan del Oro")
        self.assertEqual(
            match_legacy_name("Ixtapan", ambiguous).level, NO_MATCH)

    def test_containment_ignores_values_under_five_chars(self):
        rows = candidates("Tulancingo de Bravo")
        self.assertEqual(match_legacy_name("Tula", rows).level, NO_MATCH)

    def test_without_scope_there_is_no_search(self):
        match = match_legacy_name("Cuajimalpa", None)
        self.assertEqual(match.level, NO_SCOPE)
        self.assertIsNone(match.candidate)


class VerdictTests(SimpleTestCase):

    def test_type3_signal_beats_an_approximate_match(self):
        for level in (FUZZY, CONTAINED, NO_MATCH):
            self.assertEqual(
                verdict_for(level, "colonia", TEMPLATE_LOCALITY), TO_DETAILS)

    def test_type3_signal_does_not_beat_an_exact_match(self):
        self.assertEqual(
            verdict_for(EXACT, "zona", TEMPLATE_LOCALITY), FILL)

    def test_type3_signal_does_not_apply_to_municipalities(self):
        """«El Barrio de la Soledad» y «Tepeji del Río» son nombres
        oficiales: en el catálogo cerrado de municipios la palabra no
        delata una colonia."""
        self.assertEqual(
            verdict_for(FUZZY, "barrio", TEMPLATE_MUNICIPALITY), FILL)
        self.assertEqual(
            verdict_for(CONTAINED, "rio", TEMPLATE_MUNICIPALITY), FILL)

    def test_homonym_is_emptied(self):
        self.assertEqual(
            verdict_for(HOMONYM, "", TEMPLATE_LOCALITY), EMPTY)


class CandidateIndexTests(SyntheticCartography, TestCase):
    """El catálogo de candidatos es el mismo que ve el motor."""

    def test_localities_skip_retired_and_placeholders(self):
        names = {c.name for c in CandidateIndex().localities(self.west.id)}
        self.assertIn(self.only_one.name, names)
        self.assertNotIn(self.retired.name, names)
        self.assertNotIn(self.placeholder.name, names)
