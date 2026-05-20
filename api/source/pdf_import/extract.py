"""Fase 1 — Extracción del crudo de los PDF legados.

Descarga todos los ``NoteFile`` ``.pdf`` de cada nota candidata,
extrae el texto con coordenadas (PyMuPDF) y lo persiste en
``Article.html_content``. NO llama a Gemini: eso es la Fase 2.
Idempotente: si el Article de import ya tiene crudo, no re-descarga.
"""

import json

from django.conf import settings
from tqdm import tqdm

from source.models import Article, Note
from source.pdf_import.utils import (
    MIN_TEXT_CHARS,
    alnum_char_count,
    article_has_content,
    extract_blocks,
    get_synthetic_scraped_record,
    resolve_pdf_bytes,
)


class PdfTextExtractor:
    """Recorre notas legadas sin contenido y persiste su crudo."""

    def __init__(self) -> None:
        self.processed = 0
        self.discarded_image_only = 0
        self.skipped_no_pdf = 0
        self.errors: list[str] = []

    # ------------------------------------------------------------------
    # Selección
    # ------------------------------------------------------------------
    def get_notes(self, limit: int | None = None) -> list[Note]:
        """Notas no-Jornada, con PDF y sin Article con contenido.

        El "sin contenido" se afina en Python (filtrado exacto sobre el
        JSON vacío ``[]``, mismo criterio que ``reclassify_legal``).
        """
        qs = (
            Note.objects
            .exclude(source_id=settings.LAJORNADA_SOURCE_ID)
            .filter(files__file__iendswith=".pdf")
            .distinct()
            .prefetch_related("files", "articles")
        )
        notes: list[Note] = []
        for note in qs:
            if self._has_article_with_content(note):
                continue
            notes.append(note)
            if limit and len(notes) >= limit:
                break
        return notes

    @staticmethod
    def _has_article_with_content(note: Note) -> bool:
        return any(article_has_content(art) for art in note.articles.all())

    # ------------------------------------------------------------------
    # Proceso por nota
    # ------------------------------------------------------------------
    def run(self, limit: int | None = None) -> None:
        notes = self.get_notes(limit)
        if not notes:
            print("No hay notas legadas pendientes de extracción")
            return
        for note in tqdm(notes, desc="pdf extract"):
            try:
                self._process_note(note)
            except Exception as e:  # noqa: BLE001 - backfill robusto
                self.errors.append(f"Note {note.id}: {e}")
        self._print_summary()

    def _process_note(self, note: Note) -> None:
        pdf_files = [
            nf for nf in note.files.all()
            if nf.file and nf.file.name.lower().endswith(".pdf")
        ]
        if not pdf_files:
            self.skipped_no_pdf += 1
            return

        import_uid = f"pdf-note-{note.id}"

        # Tender a 1:1: borrar Articles vacíos (sin paragraphs/images)
        # que NO sean el de import.
        self._delete_empty_articles(note, import_uid)

        existing = Article.objects.filter(
            uid=import_uid, source=note.source).first()
        if existing and existing.html_content:
            # Ya tiene crudo: listo para Fase 2 (idempotente).
            self.processed += 1
            return

        all_blocks: list[dict] = []
        for nf in pdf_files:
            pdf_bytes = resolve_pdf_bytes(nf)
            blocks = extract_blocks(pdf_bytes)
            fname = nf.file.name.rsplit("/", 1)[-1]
            for block in blocks:
                block["file"] = fname
            all_blocks.extend(blocks)

        if alnum_char_count(all_blocks) < MIN_TEXT_CHARS:
            # Foto/captura solo-imagen: se descarta sin crear Article.
            self.discarded_image_only += 1
            return

        self._save_raw_article(note, import_uid, all_blocks, existing)
        self.processed += 1

    @staticmethod
    def _delete_empty_articles(note: Note, import_uid: str) -> None:
        for art in list(note.articles.all()):
            if art.uid == import_uid:
                continue
            if article_has_content(art):
                continue
            art.delete()

    @staticmethod
    def _save_raw_article(
        note: Note, import_uid: str, blocks: list[dict],
        existing: Article | None,
    ) -> None:
        article = existing or Article(uid=import_uid, source=note.source)
        article.scraped = get_synthetic_scraped_record(note.source)
        article.note = note
        article.url = note.link or ""
        article.published_date = note.date
        article.pages = note.pages
        article.section = note.section
        article.title = note.title  # provisional; Fase 2 lo refina
        article.html_content = json.dumps(blocks, ensure_ascii=False)
        article.save()

    def _print_summary(self) -> None:
        print(
            f"Extracción: {self.processed} con crudo | "
            f"{self.discarded_image_only} solo-imagen descartadas | "
            f"{self.skipped_no_pdf} sin PDF | "
            f"{len(self.errors)} errores"
        )
        for err in self.errors:
            print("  -", err)
