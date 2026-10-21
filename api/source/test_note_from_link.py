"""Nota desde enlace (`note_from_link`, `link_match`) y sus endpoints.

Sin red y sin Gemini: el raspado no se alcanza (los artículos del día ya
están en la base) y cada llamada a la IA va parcheada.
"""

import datetime
import tempfile
from types import SimpleNamespace
from unittest import mock

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import TestCase
from rest_framework.test import APIClient

from profile_auth.models import User
from source import link_match as lm
from source import note_from_link as nfl
from source.criteria.first import FirstCriteriaManager
from source.criteria.pre_capture import PreCaptureManager
from source.criteria.second import SecondCriteriaManager
from source.models import Article, Note, NoteFile, ScrapedRecord, Source
from source.pdf_import.utils import get_synthetic_scraped_record
from source.scraper.articles import CriteriaError
from source.scraper.reforma import ReformaManagerScraper
from work_flux.test_helpers import make_status

DAY = datetime.date(2025, 8, 10)
WEB_TITLE = "Cuestiona filme densificación de SAC Granaditas"
PRINT_TITLE = "Cuestiona filme la densificación"
WEB_LINK = ("https://www.reforma.com/cuestiona-filme-densificacion-de-"
            "sac-granaditas/ar3053228")


class SourcesMixin:
    """Las tres fuentes con su `main_url` real, más un día de Reforma."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.reforma = Source.objects.create(
            name="Reforma", main_url="https://www.reforma.com")
        cls.jornada = Source.objects.create(
            name="La Jornada", main_url="https://www.jornada.com.mx/")
        cls.proceso = Source.objects.create(
            name="Proceso", main_url="https://www.proceso.com.mx")
        cls.record = ScrapedRecord.objects.create(
            source=cls.reforma, from_date=DAY, to_date=DAY, data={})

    @classmethod
    def make_article(cls, uid: str, title: str, url: str | None = None,
                     **kwargs) -> Article:
        values = {"section": "Ciudad", "published_date": DAY,
                  "paragraphs": ["Párrafo."], "scraped": cls.record}
        values.update(kwargs)
        return Article.objects.create(
            uid=uid, title=title, source=cls.reforma,
            url=url or f"https://busquedas.gruporeforma.com/{uid}",
            **values)


def gemini_answer(answer: dict) -> mock.Mock:
    request = mock.Mock(last_error=None)
    request.send_gemini_prompt.return_value = answer
    return request


class NormalizeTests(TestCase):

    def test_normalize_title(self) -> None:
        cases = {
            "Cuestiona filme la densificación": "cuestiona filme la "
                                                "densificacion",
            "Se­gundo Pi­so": "segundo piso",
            "Policía en frontera sur obedece ¡al crimen!":
                "policia en frontera sur obedece al crimen",
            "«Exigen», dicen: ¿y la consulta?": "exigen dicen y la consulta",
            "  Doble   espacio_y guion  ": "doble espacio y guion",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(lm.normalize_title(raw), expected)

    def test_normalize_url(self) -> None:
        base = "jornada.com.mx/2025/01/12/politica/009n2pol"
        for url in (
                "https://www.jornada.com.mx/2025/01/12/politica/009n2pol",
                "http://jornada.com.mx/2025/01/12/politica/009n2pol/",
                "HTTPS://WWW.Jornada.com.mx/2025/01/12/Politica/009n2pol"):
            with self.subTest(url=url):
                self.assertEqual(lm.normalize_url(url), base)
        web_view = ("https://busquedas.gruporeforma.com/reforma/"
                    "iWebView.aspx?Coleccion=1066&Folio=123&TipoTrans=8")
        self.assertEqual(
            lm.normalize_url(web_view),
            lm.normalize_url(web_view.lower()))
        self.assertNotEqual(
            lm.normalize_url(web_view),
            lm.normalize_url(web_view.replace("Folio=123", "Folio=124")))


class SourceResolutionTests(SourcesMixin, TestCase):

    def test_resolve_source(self) -> None:
        cases = {
            "https://www.jornada.com.mx/2025/01/12/politica/009n2pol":
                self.jornada,
            WEB_LINK: self.reforma,
            "https://www.proceso.com.mx/nacional/2025/12/1/x.html":
                self.proceso,
            "https://proceso.pressreader.com/proceso/20251201/page/38":
                self.proceso,
            "https://web.jornada.com.mx/2025/01/12/politica/009n2pol":
                self.jornada,
        }
        for link, source in cases.items():
            with self.subTest(link=link):
                self.assertEqual(nfl.resolve_source(link), source)

    def test_unknown_domain(self) -> None:
        with self.assertRaises(nfl.LinkNotFetchable) as ctx:
            nfl.resolve_source("https://www.eluniversal.com.mx/nota")
        self.assertIn("eluniversal.com.mx", ctx.exception.reason)

    def test_link_fetchable(self) -> None:
        Source.objects.create(
            name="Ojarasca (La Jornada)",
            main_url="https://ojarasca.jornada.com.mx/")
        cases = {
            WEB_LINK: True,
            "https://web.jornada.com.mx/2025/01/12/politica/x": True,
            "https://ojarasca.jornada.com.mx/2025/01/x": False,
            "https://www.eluniversal.com.mx/nota": False,
            "": False,
            None: False,
        }
        for link, expected in cases.items():
            with self.subTest(link=link):
                self.assertIs(nfl.is_link_fetchable(link), expected)

    def test_edition_date(self) -> None:
        day = datetime.date(2025, 12, 15)
        self.assertEqual(
            nfl.edition_date(self.proceso, day), datetime.date(2025, 12, 1))
        self.assertEqual(nfl.edition_date(self.reforma, day), day)
        self.assertEqual(nfl.edition_date(self.jornada, day), day)


class MatcherTests(SourcesMixin, TestCase):

    def setUp(self) -> None:
        self.report = nfl.PipelineReport()
        self.neighbours = [
            self.make_article(f"n{idx}", f"Nota vecina número {idx} del día")
            for idx in range(25)]

    def match(self, title: str = WEB_TITLE, link: str = WEB_LINK,
              candidates: list | None = None) -> Article | None:
        candidates = candidates or list(
            Article.objects.filter(source=self.reforma))
        return nfl.match_article(candidates, link, title, self.report)

    def test_by_url(self) -> None:
        target = self.make_article("t", "Otro título", url=WEB_LINK + "/")
        self.assertEqual(self.match(), target)
        self.assertEqual(self.report.match["by"], "url")

    @mock.patch.object(lm, "make_gemini_request")
    def test_by_exact_title(self, gemini: mock.Mock) -> None:
        target = self.make_article("t", "Cuestiona filme densificación "
                                        "de SAC ¡Granaditas!")
        self.assertEqual(self.match(), target)
        self.assertEqual(self.report.match["by"], "title")
        gemini.assert_not_called()

    @mock.patch.object(lm, "make_gemini_request")
    def test_by_containment(self, gemini: mock.Mock) -> None:
        target = self.make_article("t", "Cuestiona filme densificación")
        self.make_article("short", "Cuestiona filme")
        self.assertEqual(self.match(), target)
        self.assertEqual(self.report.match["by"], "containment")
        gemini.assert_not_called()

    @mock.patch.object(lm, "make_gemini_request")
    def test_containment_ignores_stopwords(self, gemini: mock.Mock) -> None:
        # Tres palabras contenidas, pero solo dos con contenido.
        self.make_article("t", "Densificación de SAC")
        gemini.return_value = gemini_answer(
            {"matched": False, "reason": "Ninguna coincide."})
        self.assertIsNone(self.match())
        self.assertEqual(self.report.match["by"], "gemini")
        gemini.assert_called_once()

    @mock.patch.object(lm, "make_gemini_request")
    def test_fuzzy_above_threshold(self, gemini: mock.Mock) -> None:
        target = self.make_article(
            "t", "Cuestiona filme densificacion en SAC Granaditas")
        self.assertEqual(self.match(), target)
        self.assertEqual(self.report.match["by"], "title_fuzzy")
        self.assertGreaterEqual(
            self.report.match["ratio"], lm.TITLE_MATCH_THRESHOLD)
        gemini.assert_not_called()

    @mock.patch.object(lm, "make_gemini_request")
    def test_gemini_picks_candidate(self, gemini: mock.Mock) -> None:
        target = self.make_article("t", PRINT_TITLE)
        gemini.return_value = gemini_answer(
            {"matched": True, "candidate": 1, "reason": "Mismo filme."})
        self.assertEqual(self.match(), target)
        self.assertEqual(self.report.match["by"], "gemini")
        self.assertLess(
            self.report.match["ratio"], lm.TITLE_MATCH_THRESHOLD)
        content = gemini.return_value.send_gemini_prompt.call_args.args[0]
        listed = [line for line in content.splitlines()
                  if line[:1].isdigit()]
        # Ordenadas por parecido, y solo las primeras veinte.
        self.assertEqual(listed[0], f"1. {PRINT_TITLE} (sección: Ciudad)")
        self.assertEqual(len(listed), lm.GEMINI_MAX_CANDIDATES)

    @mock.patch.object(lm, "make_gemini_request")
    def test_gemini_answers_none(self, gemini: mock.Mock) -> None:
        self.make_article("t", PRINT_TITLE)
        gemini.return_value = gemini_answer(
            {"matched": False, "candidate": None,
             "reason": "Ninguna habla del filme."})
        self.assertIsNone(self.match())
        self.assertEqual(self.report.match["best_title"], PRINT_TITLE)
        self.assertEqual(
            self.report.match["gemini_reason"], "Ninguna habla del filme.")

    @mock.patch.object(lm, "make_gemini_request")
    def test_gemini_out_of_range_is_none(self, gemini: mock.Mock) -> None:
        self.make_article("t", PRINT_TITLE)
        gemini.return_value = gemini_answer(
            {"matched": True, "candidate": 99, "reason": "?"})
        self.assertIsNone(self.match())


class ApiTests(SourcesMixin, TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(
            username="editor", email="editor@example.test", password="x")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.status = make_status("pre_captured", "register")

    def alta(self, **extra) -> dict:
        payload = {"title": WEB_TITLE, "date": DAY.isoformat(),
                   "source": self.reforma.id, **extra}
        return self.client.post("/api/note/", payload, format="json")

    def make_note(self, **kwargs) -> Note:
        values = {"title": WEB_TITLE, "date": DAY, "source": self.reforma,
                  "link": WEB_LINK, "status_register": self.status}
        values.update(kwargs)
        return Note.objects.create(**values)

    @mock.patch.object(nfl.threading, "Thread")
    def test_alta_unknown_domain_saves_without_pipeline(
            self, thread: mock.Mock) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            response = self.alta(link="https://www.eluniversal.com.mx/x")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], nfl.NOT_FETCHABLE_MSG)
        self.assertFalse(response.data["link_fetchable"])
        note = Note.objects.get()
        self.assertEqual(note.source, self.reforma)
        thread.assert_not_called()

    @mock.patch.object(nfl.threading, "Thread")
    def test_alta_source_without_scraper_saves(
            self, thread: mock.Mock) -> None:
        Source.objects.create(
            name="Ojarasca (La Jornada)",
            main_url="https://ojarasca.jornada.com.mx/")
        with self.captureOnCommitCallbacks(execute=True):
            response = self.alta(
                link="https://ojarasca.jornada.com.mx/2025/08/x")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], nfl.NOT_FETCHABLE_MSG)
        self.assertEqual(Note.objects.count(), 1)
        thread.assert_not_called()

    def test_alta_duplicate_creates_nothing(self) -> None:
        other = self.make_note(title="Ya capturada")
        self.make_article("t", PRINT_TITLE, url=WEB_LINK, note=other)
        response = self.alta(link=WEB_LINK)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], nfl.DUPLICATE_MSG)
        self.assertEqual(response.data["note"], other.id)
        self.assertEqual(Note.objects.count(), 1)

    @mock.patch.object(nfl.threading, "Thread")
    def test_alta_launches_thread(self, thread: mock.Mock) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            response = self.alta(link=WEB_LINK)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], nfl.QUEUED_MSG)
        self.assertTrue(response.data["link_fetchable"])
        note_id = response.data["id"]
        self.assertEqual(thread.call_args.kwargs["args"],
                         (note_id, self.user.id))
        thread.return_value.start.assert_called_once()
        nfl._running.discard(note_id)

    def fetch(self, note: Note):
        return self.client.post(f"/api/note/{note.id}/fetch_from_link/")

    def test_fetch_without_link(self) -> None:
        response = self.fetch(self.make_note(link=None))
        self.assertEqual(response.status_code, 400)

    @mock.patch.object(nfl.threading, "Thread")
    def test_fetch_unknown_domain_is_not_an_error(
            self, thread: mock.Mock) -> None:
        note = self.make_note(link="https://www.eluniversal.com.mx/x")
        response = self.fetch(note)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], nfl.NOT_FETCHABLE_MSG)
        thread.assert_not_called()
        self.assertNotIn(note.id, nfl._running)

    def test_fetch_with_article(self) -> None:
        note = self.make_note()
        self.make_article("t", PRINT_TITLE, note=note)
        self.assertEqual(self.fetch(note).status_code, 400)

    def test_fetch_article_of_other_note(self) -> None:
        other = self.make_note(title="Ya capturada")
        self.make_article("t", PRINT_TITLE, url=WEB_LINK, note=other)
        response = self.fetch(self.make_note())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], nfl.DUPLICATE_MSG)

    @mock.patch.object(nfl.threading, "Thread")
    def test_fetch_launches_once(self, thread: mock.Mock) -> None:
        note = self.make_note()
        response = self.fetch(note)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], nfl.QUEUED_MSG)
        # El hilo aún no termina (nunca arrancó): el segundo clic se
        # rechaza en vez de lanzar otra corrida.
        self.assertEqual(self.fetch(note).status_code, 400)
        nfl._running.discard(note.id)

    def test_pre_capture_without_article(self) -> None:
        note = self.make_note()
        response = self.client.post(
            f"/api/note/{note.id}/start_pre_capture/")
        self.assertEqual(response.status_code, 400)


def fake_build(response_parsed=None, last_error=None):
    """Sustituye `build_gemini_request`: deja un request sin red."""
    def build(manager, *args, **kwargs):
        manager.classify_request = SimpleNamespace(
            last_error=last_error,
            response=SimpleNamespace(parsed=response_parsed))
    return build


class GeminiMixin:
    """Las tres pasadas sin red: cada test decide qué responde cada una."""

    def patch_builders(self) -> None:
        for manager in (FirstCriteriaManager, SecondCriteriaManager,
                        PreCaptureManager):
            patcher = mock.patch.object(
                manager, "build_gemini_request", autospec=True,
                side_effect=fake_build())
            patcher.start()
            self.addCleanup(patcher.stop)

    def patch_criteria(self, manager, **kwargs) -> mock.Mock:
        patcher = mock.patch.object(manager, "get_ai_criteria", **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def fail_second(self, article: Article) -> None:
        self.patch_criteria(FirstCriteriaManager)
        self.patch_criteria(
            SecondCriteriaManager,
            side_effect=CriteriaError(article, "No response AI service",
                                      cause="503 UNAVAILABLE"))

    def empty_precapture(self) -> None:
        self.patch_criteria(FirstCriteriaManager)
        self.patch_criteria(SecondCriteriaManager)
        PreCaptureManager.build_gemini_request.side_effect = fake_build(
            response_parsed=[])

        def empty(article):
            raise CriteriaError(article, "No response AI service")
        self.patch_criteria(PreCaptureManager, side_effect=empty)


class ChainTests(GeminiMixin, SourcesMixin, TestCase):

    def setUp(self) -> None:
        self.status = make_status("pre_captured", "register")
        self.note = Note.objects.create(
            title=WEB_TITLE, date=DAY, source=self.reforma, link=WEB_LINK,
            status_register=self.status)
        self.article = self.make_article("t", PRINT_TITLE, note=self.note)
        self.report = nfl.PipelineReport()
        self.patch_builders()

    def run_chain(self) -> None:
        nfl.run_gemini_chain(self.note, self.article, self.report)

    def test_stops_at_first_failure(self) -> None:
        self.fail_second(self.article)
        precapture = self.patch_criteria(PreCaptureManager)
        self.run_chain()
        self.assertEqual(self.report.stages, ["first"])
        self.assertEqual(len(self.report.errors), 1)
        self.assertTrue(self.report.errors[0].startswith("second:"))
        self.assertEqual(self.report.failed_stage, "second")
        precapture.assert_not_called()
        comment = nfl.outcome_comment(self.report)
        self.assertIn(nfl.STAGE_LABELS["second"], comment)
        self.assertIn("503 UNAVAILABLE", comment)
        self.assertIn(f"«{nfl.FETCH_BUTTON}»", comment)

    def test_empty_precapture_is_not_an_error(self) -> None:
        self.empty_precapture()
        self.run_chain()
        self.assertEqual(self.report.errors, [])
        self.assertIsNone(self.report.failed_stage)
        self.assertIn("empty_precapture", self.report.flags)
        self.article.refresh_from_db()
        self.assertFalse(self.article.errors)
        comment = nfl.outcome_comment(self.report)
        self.assertIn("sin menciones relevantes", comment)
        self.assertNotIn("falló", comment)

    def test_precapture_without_response_is_an_error(self) -> None:
        self.patch_criteria(FirstCriteriaManager)
        self.patch_criteria(SecondCriteriaManager)
        PreCaptureManager.build_gemini_request.side_effect = fake_build(
            last_error="429 RESOURCE_EXHAUSTED")
        self.patch_criteria(
            PreCaptureManager,
            side_effect=CriteriaError(self.article, "No response AI service"))
        self.run_chain()
        self.assertEqual(len(self.report.errors), 1)
        self.assertEqual(self.report.failed_stage, "precapture")
        self.assertNotIn("empty_precapture", self.report.flags)

    def test_frozen_skips_precapture(self) -> None:
        self.note.frozen_pre_capture = True
        self.patch_criteria(FirstCriteriaManager)
        self.patch_criteria(SecondCriteriaManager)
        precapture = self.patch_criteria(PreCaptureManager)
        self.run_chain()
        precapture.assert_not_called()
        self.assertEqual(self.report.stages, ["first", "second"])
        self.assertIn("frozen", self.report.flags)
        self.assertEqual(self.report.errors, [])

    def test_runs_only_missing_stages(self) -> None:
        self.article.criteria = {"projects": []}
        self.article.save()
        first = self.patch_criteria(FirstCriteriaManager)
        self.patch_criteria(SecondCriteriaManager)
        self.patch_criteria(PreCaptureManager)
        self.run_chain()
        first.assert_not_called()
        self.assertEqual(self.report.reused, ["first"])
        self.assertEqual(self.report.stages, ["second", "precapture"])
        comment = nfl.outcome_comment(self.report)
        self.assertIn(
            "se reutilizó la clasificación del lote: primera pasada", comment)

    def test_reuses_batch_precapture(self) -> None:
        self.article.criteria = {"projects": []}
        self.article.second_criteria = {"projects": []}
        self.article.pre_capture = [{"project_full": {}}]
        self.article.save()
        managers = (FirstCriteriaManager, SecondCriteriaManager,
                    PreCaptureManager)
        calls = [self.patch_criteria(manager) for manager in managers]
        with mock.patch.object(
                PreCaptureManager, "save_criteria_results") as save:
            self.run_chain()
        for call in calls:
            call.assert_not_called()
        save.assert_called_once_with(None, None, self.article)
        self.assertEqual(self.report.stages, [])
        self.assertEqual(
            self.report.reused, ["first", "second", "precapture"])
        comment = nfl.outcome_comment(self.report)
        self.assertTrue(comment.startswith("Artículo y precaptura listos"))
        self.assertIn("primera pasada, segunda pasada y precaptura", comment)

    def test_batch_precapture_not_copied_over_mentions(self) -> None:
        self.article.criteria = {"projects": []}
        self.article.second_criteria = {"projects": []}
        self.article.pre_capture = [{"project_full": {}}]
        self.article.save()
        with mock.patch.object(Note, "mentions") as mentions, \
                mock.patch.object(
                    PreCaptureManager, "save_criteria_results") as save:
            mentions.exists.return_value = True
            self.run_chain()
        save.assert_not_called()
        self.assertIn("precapture_exists", self.report.flags)
        comment = nfl.outcome_comment(self.report)
        self.assertIn("precaptura ya existente", comment)
        self.assertNotIn("precaptura listo", comment)

    def test_success_comment_says_how_it_matched(self) -> None:
        cases = {
            "gemini": "emparejada por Gemini con «Impreso»",
            "containment": "emparejada por contención con «Impreso»",
            "title_fuzzy": "emparejada por similitud con «Impreso»",
        }
        for by, expected in cases.items():
            with self.subTest(by=by):
                report = nfl.PipelineReport(
                    match={"by": by, "best_title": "Impreso"})
                self.assertIn(expected, nfl.success_comment(report))
        for by in ("url", "title"):
            with self.subTest(by=by):
                report = nfl.PipelineReport(match={"by": by})
                self.assertNotIn(
                    "emparejada", nfl.success_comment(report))

    def test_signature_carries_time_so_retries_stack(self) -> None:
        times = [datetime.datetime(2026, 10, 20, 10, 5),
                 datetime.datetime(2026, 10, 20, 10, 9)]
        with mock.patch.object(nfl.timezone, "localtime",
                               side_effect=times):
            first, second = nfl.sign("Igual."), nfl.sign("Igual.")
        self.assertEqual(first, "20/10/2026 10:05 - Sistema: Igual.")
        self.note.add_comment(first)
        self.note.add_comment(second)
        self.assertIn(first, self.note.comments)
        self.assertIn(second, self.note.comments)

    def test_failure_comment_names_best_candidate(self) -> None:
        note = Note.objects.create(
            title="Algo que no existe", date=DAY, source=self.reforma,
            link="https://www.reforma.com/algo-que-no-existe/ar1",
            status_register=self.status)
        with mock.patch.object(lm, "make_gemini_request") as gemini:
            gemini.return_value = gemini_answer(
                {"matched": False, "reason": "Ninguna coincide."})
            comment = nfl.run_note_pipeline(note)
        note.refresh_from_db()
        self.assertTrue(comment.startswith(nfl.NOT_FOUND_MSG))
        self.assertIn(f"«{PRINT_TITLE}»", comment)
        self.assertIn(comment, note.comments)
        self.assertFalse(note.articles.exists())
        self.assertEqual(note.status_register, self.status)


class FillNoteTests(SourcesMixin, TestCase):

    @mock.patch.object(nfl, "run_gemini_chain")
    def test_keeps_filled_fields_and_status(self, chain: mock.Mock) -> None:
        status = make_status("pre_captured", "register")
        # Sin generador de adjunto: la fuente de prueba no está registrada.
        source = Source.objects.create(
            name="Sin generador", main_url="https://example.test")
        note = Note.objects.create(
            title=WEB_TITLE, date=DAY, source=source, link=WEB_LINK,
            subtitle="Subtítulo del editor", status_register=status)
        article = self.make_article(
            "t", PRINT_TITLE, subtitle="Subtítulo impreso",
            author="Reportera", pages="12")
        prepared = nfl.PreparedArticle(
            source=source, article=article, report=nfl.PipelineReport())
        report = nfl.fill_note_from_article(note, prepared)
        note.refresh_from_db()
        self.assertEqual(note.subtitle, "Subtítulo del editor")
        self.assertEqual(note.author, "Reportera")
        self.assertEqual(note.pages, "12")
        self.assertEqual(note.status_register, status)
        self.assertEqual(note.articles.get(), article)
        self.assertIn("no_generator", report.flags)
        chain.assert_called_once()


class RollbackTests(GeminiMixin, SourcesMixin, TestCase):
    """Una pasada de Gemini que falla suelta el artículo de la nota."""

    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory(prefix="ocsa_link_")
        self.addCleanup(temp_dir.cleanup)
        # Mismo truco que source/tests.py: el storage del campo se fija al
        # declararlo y no lo alcanza un override_settings.
        field = NoteFile._meta.get_field("file")
        original_storage = field.storage
        self.storage = FileSystemStorage(location=temp_dir.name)
        field.storage = self.storage
        self.addCleanup(setattr, field, "storage", original_storage)

        self.status = make_status("pre_captured", "register")
        self.note = Note.objects.create(
            title=WEB_TITLE, date=DAY, source=self.reforma, link=WEB_LINK,
            status_register=self.status)
        self.article = self.make_article("t", PRINT_TITLE, url=WEB_LINK)
        self.patch_builders()
        generator = mock.patch(
            "source.attachment.get_attachment_generator",
            return_value=object)
        generator.start()
        self.addCleanup(generator.stop)

    def fake_generate(self, article: Article, note: Note) -> NoteFile:
        note_file = NoteFile(note=note)
        note_file.file.save(
            "generado.pdf", ContentFile(b"%PDF generado"), save=True)
        self.generated = note_file.file.name
        return note_file

    def run_pipeline(self) -> str:
        with mock.patch("source.attachment.generate_attachment",
                        side_effect=self.fake_generate):
            return nfl.run_note_pipeline(self.note)

    def test_failed_stage_unlinks_and_drops_generated_file(self) -> None:
        self.fail_second(self.article)
        comment = self.run_pipeline()
        self.article.refresh_from_db()
        self.assertIsNone(self.article.note_id)
        self.assertEqual(self.article.paragraphs, ["Párrafo."])
        self.assertFalse(self.note.files.exists())
        self.assertFalse(self.storage.exists(self.generated))
        self.assertIn(nfl.STAGE_LABELS["second"], comment)
        self.assertIn(nfl.FETCH_BUTTON, comment)
        self.note.refresh_from_db()
        self.assertIn(comment, self.note.comments)

    def test_failed_stage_keeps_editor_file(self) -> None:
        editor_file = NoteFile(note=self.note)
        editor_file.file.save(
            "editor.pdf", ContentFile(b"%PDF editor"), save=True)
        self.fail_second(self.article)
        self.run_pipeline()
        self.article.refresh_from_db()
        self.assertIsNone(self.article.note_id)
        self.assertEqual(list(self.note.files.all()), [editor_file])
        self.assertTrue(self.storage.exists(editor_file.file.name))

    def test_retry_after_rollback_relinks(self) -> None:
        self.fail_second(self.article)
        self.run_pipeline()
        SecondCriteriaManager.get_ai_criteria.side_effect = None
        self.patch_criteria(PreCaptureManager)
        comment = self.run_pipeline()
        self.article.refresh_from_db()
        self.assertEqual(self.article.note_id, self.note.id)
        self.assertEqual(self.note.files.count(), 1)
        self.assertNotIn("falló", comment)

    def test_empty_precapture_keeps_link(self) -> None:
        self.empty_precapture()
        comment = self.run_pipeline()
        self.article.refresh_from_db()
        self.assertEqual(self.article.note_id, self.note.id)
        self.assertEqual(self.note.files.count(), 1)
        self.assertIn("sin menciones relevantes", comment)


class ListingRuleTests(SourcesMixin, TestCase):
    """Con lote real no se vuelve a raspar el listado del día."""

    NO_BATCH_DAY = datetime.date(2025, 8, 11)

    def setUp(self) -> None:
        patcher = mock.patch.object(nfl, "scrape_day_listing")
        self.scrape = patcher.start()
        self.addCleanup(patcher.stop)
        self.synthetic = get_synthetic_scraped_record(self.reforma)

    def prepare(self, day: datetime.date) -> nfl.PreparedArticle:
        return nfl.prepare_article(WEB_LINK, day, WEB_TITLE)

    def test_batch_day_without_articles_fails(self) -> None:
        with self.assertRaises(nfl.NoteFromLinkError) as ctx:
            self.prepare(DAY)
        self.assertIn("lote", ctx.exception.reason)
        self.scrape.assert_not_called()

    @mock.patch.object(lm, "make_gemini_request")
    def test_batch_day_without_match_fails(self, gemini) -> None:
        self.make_article("other", "Nada que ver con el filme")
        gemini.return_value = gemini_answer(
            {"matched": False, "reason": "Ninguna coincide."})
        with self.assertRaises(nfl.NoteFromLinkError):
            self.prepare(DAY)
        self.scrape.assert_not_called()

    def test_batch_day_keeps_pdf_import_candidates(self) -> None:
        legacy = self.make_article(
            "pdf-note-1", WEB_TITLE, scraped=self.synthetic)
        prepared = self.prepare(DAY)
        self.assertEqual(prepared.article, legacy)
        self.scrape.assert_not_called()

    def test_synthetic_record_is_not_a_batch(self) -> None:
        legacy_day = datetime.date(2020, 3, 1)
        self.assertIsNone(nfl.covering_record(self.reforma, legacy_day))
        self.assertEqual(nfl.covering_record(self.reforma, DAY), self.record)

    def test_day_without_batch_scrapes_listing(self) -> None:
        # Un artículo de pdf_import no prueba que el día esté listado.
        self.make_article(
            "pdf-note-2", "Nota legada", scraped=self.synthetic,
            published_date=self.NO_BATCH_DAY)

        def scrape(source, day):
            listed = self.make_article(
                "listed", WEB_TITLE, scraped=self.synthetic,
                published_date=day)
            return [listed]
        self.scrape.side_effect = scrape
        prepared = self.prepare(self.NO_BATCH_DAY)
        self.scrape.assert_called_once_with(self.reforma, self.NO_BATCH_DAY)
        self.assertEqual(prepared.article.uid, "listed")
        self.assertIn("listing", prepared.report.stages)

    def test_day_already_listed_does_not_scrape(self) -> None:
        listed = self.make_article(
            "listed", WEB_TITLE, scraped=self.synthetic,
            published_date=self.NO_BATCH_DAY)
        prepared = self.prepare(self.NO_BATCH_DAY)
        self.scrape.assert_not_called()
        self.assertEqual(prepared.article, listed)


class ProcesoMonthTests(SourcesMixin, TestCase):
    """Proceso es mensual: candidatos y lote se buscan en el mes entero."""

    LINK = "https://proceso.pressreader.com/proceso/20251201/page/38"
    NOTE_DAY = datetime.date(2025, 12, 15)

    def setUp(self) -> None:
        patcher = mock.patch.object(nfl, "scrape_day_listing")
        self.scrape = patcher.start()
        self.addCleanup(patcher.stop)

    def make_proceso(self, uid: str, day: datetime.date) -> Article:
        return Article.objects.create(
            uid=uid, title=f"Nota {uid} de Proceso con título", url=self.LINK,
            source=self.proceso, published_date=day,
            paragraphs=["Párrafo."],
            scraped=get_synthetic_scraped_record(self.proceso))

    def test_candidates_are_the_whole_month(self) -> None:
        first = self.make_proceso("a", datetime.date(2025, 12, 1))
        fourth = self.make_proceso("b", datetime.date(2025, 12, 4))
        self.make_proceso("c", datetime.date(2025, 11, 30))
        day = nfl.edition_date(self.proceso, self.NOTE_DAY)
        self.assertEqual(
            set(nfl.edition_articles(self.proceso, day)), {first, fourth})
        # Jornada y Reforma siguen siendo por día.
        self.assertEqual(nfl.edition_articles(self.reforma, DAY), [])

    def test_batch_touching_the_month_covers_it(self) -> None:
        batch = ScrapedRecord.objects.create(
            source=self.proceso, from_date=datetime.date(2025, 12, 10),
            to_date=datetime.date(2025, 12, 31), data={})
        day = nfl.edition_date(self.proceso, self.NOTE_DAY)
        self.assertEqual(nfl.covering_record(self.proceso, day), batch)
        self.assertIsNone(nfl.covering_record(
            self.proceso, datetime.date(2026, 1, 1)))

    def test_matches_article_dated_inside_the_month(self) -> None:
        ScrapedRecord.objects.create(
            source=self.proceso, from_date=datetime.date(2025, 12, 1),
            to_date=datetime.date(2025, 12, 31), data={})
        target = self.make_proceso("b", datetime.date(2025, 12, 4))
        prepared = nfl.prepare_article(
            self.LINK, self.NOTE_DAY, target.title)
        self.assertEqual(prepared.article, target)
        self.scrape.assert_not_called()


class OverlapTests(SourcesMixin, TestCase):
    """El registro sintético no frena un lote; uno real sí."""

    def check(self, day: datetime.date) -> bool:
        manager = ReformaManagerScraper("", "", recover_record=self.record)
        return manager.check_overlapping_records(day, day)

    def test_synthetic_record_does_not_block(self) -> None:
        get_synthetic_scraped_record(self.reforma)
        self.assertTrue(self.check(datetime.date(2020, 3, 1)))

    def test_real_batch_blocks(self) -> None:
        self.assertFalse(self.check(DAY))


class RecordArticleTests(SourcesMixin, TestCase):
    """El lote reclama del sintético los artículos que ya existían."""

    def record_uid(self, uid: str) -> None:
        manager = ReformaManagerScraper("", "", recover_record=self.batch)
        article_data = {"uid": uid, "url": f"https://x.test/{uid}",
                        "title": "Título del listado"}
        manager.record_article(article_data, "Ciudad", "20250810")

    def setUp(self) -> None:
        self.batch = ScrapedRecord.objects.create(
            source=self.reforma, from_date=DAY, to_date=DAY, data={})

    def test_reclaims_from_synthetic(self) -> None:
        synthetic = get_synthetic_scraped_record(self.reforma)
        article = self.make_article("from-link", "T", scraped=synthetic)
        self.record_uid("from-link")
        article.refresh_from_db()
        self.assertEqual(article.scraped, self.batch)

    def test_leaves_other_batch_alone(self) -> None:
        article = self.make_article("other-batch", "T")
        self.record_uid("other-batch")
        article.refresh_from_db()
        self.assertEqual(article.scraped, self.record)
