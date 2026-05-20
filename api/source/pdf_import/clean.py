"""Fase 2 — Limpieza del crudo con Gemini.

Toma los Article de import que ya tienen ``html_content`` (crudo de
Fase 1) pero aún no ``paragraphs``, y le pide a Gemini que extraiga la
nota correcta (orientado por el título real de la ``Note``) y devuelva
los campos de cabecera + párrafos.

Reutiliza ``RequestGemini`` directamente (no ``BaseCriteriaManager``:
ese contrato construye el prompt *a partir* de paragraphs; aquí los
generamos). Idempotente: no reprocesa los ya limpios ni los marcados
``not_found``.
"""

import json

from django.db.models import Q
from django.utils import timezone
from tqdm import tqdm

from source.criteria import make_gemini_request
from source.models import Article


class PdfAiCleaner:
    """Limpia el crudo de los Article de import con Gemini."""

    # Campos que se propagan a la Note solo cuando vienen vacíos
    NOTE_BACKFILL_FIELDS = (
        "title", "subtitle", "author", "section", "pages")

    def __init__(
        self, ai_engine: str | None = None, is_test: bool = False,
    ) -> None:
        self.ai_engine = ai_engine
        self.is_test = is_test
        self.prompt_name = "pdf_cleanup"
        self.version = "v1"
        self.seconds_cache = 10
        self.classify_request = None
        self.cleaned = 0
        self.not_found = 0
        self.errors: list[str] = []

    # ------------------------------------------------------------------
    # Selección
    # ------------------------------------------------------------------
    def get_articles(self, limit: int | None = None) -> list[Article]:
        # JSONField: cubrir tanto SQL NULL como [] literal.
        empty_paragraphs = Q(paragraphs__isnull=True) | Q(paragraphs=[])
        empty_images = Q(images__isnull=True) | Q(images=[])
        qs = (
            Article.objects
            .filter(uid__startswith="pdf-note-")
            .exclude(html_content__isnull=True)
            .exclude(html_content="")
            .filter(empty_paragraphs & empty_images)
            .exclude(metadata__pdf_clean="not_found")
            .select_related("note")
        )
        if limit:
            qs = qs[:limit]
        return list(qs)

    # ------------------------------------------------------------------
    # Request Gemini
    # ------------------------------------------------------------------
    def build_gemini_request(self, len_articles: int = 1) -> None:
        self.classify_request = make_gemini_request(
            self, len_articles, prompt_segment="")

    def _build_content(self, article: Article) -> str:
        note = article.note
        lines = ["## ORIENTACIÓN (extrae SOLO esta nota del crudo)"]
        lines.append(f"Título: {note.title}")
        if note.author:
            lines.append(f"Autor (capturado): {note.author}")
        if note.date:
            lines.append(f"Fecha: {note.date.isoformat()}")
        if note.section:
            lines.append(f"Sección (capturada): {note.section}")
        lines.append("")
        lines.append("## BLOQUES CRUDOS DEL/LOS PDF "
                     "(pueden traer varias notas y chrome; usa bbox)")
        blocks = json.loads(article.html_content)
        for block in blocks:
            page = block.get("page")
            bbox = block.get("bbox")
            fname = block.get("file", "")
            text = block.get("text", "").replace("\n", " / ")
            lines.append(f"[p{page} {fname} bbox={bbox}] {text}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Proceso
    # ------------------------------------------------------------------
    def run(self, limit: int | None = None) -> None:
        articles = self.get_articles(limit)
        if not articles:
            print("No hay crudo pendiente de limpieza IA")
            return
        self.build_gemini_request(len(articles))
        for article in tqdm(articles, desc="pdf cleanup"):
            try:
                self._process_article(article)
            except Exception as e:  # noqa: BLE001 - backfill robusto
                self.errors.append(f"Article {article.id}: {e}")
        if self.classify_request.errors:
            self.errors.extend(self.classify_request.errors)
        self._print_summary()

    def _process_article(self, article: Article) -> None:
        from source.base_models import PdfCleanResult

        content = self._build_content(article)
        result = self.classify_request.send_gemini_prompt(
            content, schema_clss=PdfCleanResult)
        if not result:
            self.errors.append(
                f"Article {article.id}: sin respuesta IA")
            return
        try:
            clean = PdfCleanResult.model_validate(result)
        except Exception as e:
            self.errors.append(
                f"Article {article.id}: respuesta inválida: {e}")
            return
        self._save(article, clean)

    @staticmethod
    def _mark_problematic(article: Article, reason: str) -> None:
        """Conserva html_content; sin paragraphs; fuera de reintentos."""
        metadata = article.metadata or {}
        metadata["pdf_clean"] = "not_found"
        article.metadata = metadata
        stamp = timezone.now().isoformat()
        article.errors = (article.errors or []) + [
            f"{stamp} - pdf_cleanup not_found: {reason}"]
        article.save()

    def _save(self, article: Article, clean) -> None:
        if not clean.note_found or not clean.paragraphs:
            reason = clean.not_found_reason or (
                "note_found pero sin párrafos" if clean.note_found
                else "Gemini no encontró la nota en el crudo")
            self._mark_problematic(article, reason)
            self.not_found += 1
            return

        note = article.note
        note_dirty = False
        article.paragraphs = clean.paragraphs
        for field in self.NOTE_BACKFILL_FIELDS:
            value = getattr(clean, field)
            setattr(article, field, value)
            if not getattr(note, field) and value:
                setattr(note, field, value)
                note_dirty = True
        metadata = article.metadata or {}
        metadata["pdf_detected"] = {
            "pages": clean.pages,
            "published_date": clean.published_date,
        }
        article.metadata = metadata
        article.save()
        if note_dirty:
            note.save()
        self.cleaned += 1

    def _print_summary(self) -> None:
        print(
            f"Limpieza IA: {self.cleaned} limpios | "
            f"{self.not_found} problemáticos (not_found) | "
            f"{len(self.errors)} errores"
        )
        for err in self.errors:
            print("  -", err)