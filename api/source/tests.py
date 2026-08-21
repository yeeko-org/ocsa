"""Invariante de escritura de adjuntos (`source/attachment/`).

Lo que se prueba en todos los escenarios: pase lo que pase, nunca queda
una fila `NoteFile` sin archivo real detrás, y los adjuntos previos solo
desaparecen cuando el nuevo ya está escrito.

No tocan la red: los generadores reales corren con sus llamadas de red y
de render parcheadas.
"""

import datetime
import tempfile
from typing import Callable
from unittest import mock

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import TestCase

from source.attachment import jornada, reforma
from source.attachment.base import AttachmentGenerator, GeneratedAttachment
from source.models import Article, Note, NoteFile, Source
from source.scraper.proceso import ProcesoMainScraper

Behaviour = Callable[[], GeneratedAttachment | None]

NEW_BYTES = b"%PDF-1.4 nuevo"


class FakeGenerator(AttachmentGenerator):
    """Generador de laboratorio: cada escenario inyecta su `build`."""

    source_url = "https://example.test"

    def __init__(self, article: Article, behaviour: Behaviour) -> None:
        super().__init__(article)
        self.behaviour = behaviour

    def build(self) -> GeneratedAttachment | None:
        return self.behaviour()


class AttachmentInvariantTests(TestCase):
    """Escritura de adjuntos ante fallos de red, render y storage."""

    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory(prefix="ocsa_attach_")
        self.addCleanup(temp_dir.cleanup)
        # El storage del campo se resuelve al declararlo (callable), así
        # que ya no lo alcanza un override_settings sobre STORAGES.
        self.field = NoteFile._meta.get_field("file")
        original_storage = self.field.storage
        self.field.storage = FileSystemStorage(location=temp_dir.name)
        self.addCleanup(setattr, self.field, "storage", original_storage)

        self.source = Source.objects.create(
            name="Fuente de prueba", main_url="https://example.test")
        self.note = Note.objects.create(
            title="Nota de prueba invariante", source=self.source,
            pages="OLD1", date=datetime.date(2026, 8, 21))
        self.previous = NoteFile(note=self.note)
        self.previous.file.save("old.pdf", ContentFile(b"viejo"), save=False)
        self.previous.save()
        # Sin guardar: los generadores solo leen el artículo, y guardarlo
        # exigiría un ScrapedRecord que no aporta nada al invariante.
        self.article = Article(
            uid="2026/08/21/001n1pol", source=self.source, title="Título",
            url="https://www.jornada.com.mx/2026/08/21/politica/001n1pol",
            published_date=datetime.date(2026, 8, 21))

    def current_pks(self) -> list[int]:
        return list(self.note.files.values_list("pk", flat=True))

    def assert_invariant(self) -> None:
        """Ninguna fila `NoteFile` sin bytes reales en storage."""
        empty = [row for row in self.note.files.all()
                 if not row.file or not row.file.name or not row.file.size]
        self.assertEqual(empty, [], "hay NoteFile sin archivo real")

    def assert_previous_intact(self) -> None:
        self.assertEqual(self.current_pks(), [self.previous.pk])

    def run_fake(
            self, behaviour: Behaviour, replace: bool = True
    ) -> NoteFile | None:
        return FakeGenerator(self.article, behaviour).generate(
            note=self.note, replace=replace)

    def test_network_failure_keeps_previous(self) -> None:
        """Excepción de red en `build`: no propaga ni borra el adjunto."""
        def boom() -> GeneratedAttachment:
            raise ConnectionError("conexión perdida a media descarga")

        with self.assertLogs("source.attachment.base", "ERROR"):
            result = self.run_fake(boom)
        self.assertIsNone(result)
        self.assert_invariant()
        self.assert_previous_intact()

    def test_empty_content_is_not_stored(self) -> None:
        """Respuesta vacía con éxito aparente: no se crea fila alguna."""
        result = self.run_fake(lambda: GeneratedAttachment(b"", "vacio.pdf"))
        self.assertIsNone(result)
        self.assert_invariant()
        self.assert_previous_intact()

    def test_build_returning_none_keeps_previous(self) -> None:
        """«No hay adjunto» es un desenlace válido, no un borrado."""
        result = self.run_fake(lambda: None)
        self.assertIsNone(result)
        self.assert_invariant()
        self.assert_previous_intact()

    def test_storage_write_failure_keeps_previous(self) -> None:
        """Storage caído al escribir: ni fila nueva ni pérdida de la vieja."""
        def attachment() -> GeneratedAttachment:
            return GeneratedAttachment(NEW_BYTES, "nuevo.pdf")

        with mock.patch.object(
                self.field.storage, "save",
                side_effect=OSError("storage inaccesible")):
            with self.assertLogs("source.attachment.base", "ERROR"):
                result = self.run_fake(attachment)
        self.assertIsNone(result)
        self.assert_invariant()
        self.assert_previous_intact()

    def test_replace_swaps_attachment_and_fixes_pages(self) -> None:
        """Camino feliz: un solo adjunto, el nuevo, y `pages` corregido."""
        result = self.run_fake(
            lambda: GeneratedAttachment(
                NEW_BYTES, "nuevo.pdf", page_code="NEW9"))
        self.assertIsNotNone(result)
        self.assert_invariant()
        pks = self.current_pks()
        self.assertNotIn(self.previous.pk, pks)
        self.assertEqual(len(pks), 1)
        self.assertEqual(result.file.size, len(NEW_BYTES))
        self.note.refresh_from_db(fields=["pages"])
        self.assertEqual(self.note.pages, "NEW9")

    def test_without_replace_does_not_even_build(self) -> None:
        """Con adjunto previo y `replace=False` no se descarga nada."""
        behaviour = mock.Mock(
            return_value=GeneratedAttachment(NEW_BYTES, "nuevo.pdf"))
        result = self.run_fake(behaviour, replace=False)
        self.assertIsNone(result)
        behaviour.assert_not_called()
        self.assert_invariant()
        self.assert_previous_intact()

    def test_reforma_survives_network_failure(self) -> None:
        """Reforma con la red caída: la excepción muere en `safe_build`."""
        self.article.metadata = {"paginas": [{
            "texto": "PAG-01",
            "mapeo": [{"width": 1, "height": 1, "x": 0, "y": 0}],
        }]}
        with mock.patch.object(
                reforma.requests, "post",
                side_effect=reforma.requests.exceptions.ConnectionError(
                    "sin red")) as post:
            with self.assertLogs("source.attachment.base", "ERROR"):
                result = reforma.ReformaAttachmentGenerator(
                    self.article).generate(note=self.note, replace=True)
        post.assert_called_once()
        self.assertIsNone(result)
        self.assert_invariant()
        self.assert_previous_intact()

    def test_jornada_survives_render_failure(self) -> None:
        """La Jornada con el render roto: tampoco pierde el adjunto."""
        self.article.paragraphs = ["uno"]
        with mock.patch.object(
                jornada, "build_html",
                side_effect=ValueError("marcado imposible")) as build_html:
            with self.assertLogs("source.attachment.base", "ERROR"):
                result = jornada.JornadaAttachmentGenerator(
                    self.article).generate(note=self.note, replace=True)
        build_html.assert_called_once()
        self.assertIsNone(result)
        self.assert_invariant()
        self.assert_previous_intact()


def probe_proceso_sections(scraper_date: str = "20240201") -> None:
    """
    Sonda manual: cuántas secciones y artículos trae un issue de Proceso.

    Vive dentro de una función porque `manage.py test` importa este módulo:
    suelto, disparaba un scraping real contra PressReader en cada corrida
    y quemaba el slot de sesión.
    """
    main = ProcesoMainScraper(scraper_date)
    print("secciones:", list(main.sections_dict.keys()))
    total = sum(len(s["articles"]) for s in main.sections_dict.values())
    print("total artículos:", total)
