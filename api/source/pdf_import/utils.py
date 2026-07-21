"""Helpers compartidos por las dos fases de la ingesta desde PDF."""

from datetime import date

import fitz  # PyMuPDF
import requests
from django.conf import settings

from source.models import Article, NoteFile, ScrapedRecord, Source
from source.scraper.scraper_base import REQUESTS_DEFAULT_HEADERS

# Compuerta entre fase 1 y fase 2: si el crudo extraído tiene menos
# caracteres alfanuméricos que esto, el PDF es foto/captura (solo
# imagen) y se descarta. Bajo a propósito: a veces la nota es una
# imagen con un pie de foto corto que igual nos sirve.
MIN_TEXT_CHARS = 80

# Fechas del ScrapedRecord sintético por fuente (solo referencia de
# visualización en el frontend; acepta notas de fechas posteriores).
LEGACY_FROM_DATE = date(2017, 1, 1)
LEGACY_TO_DATE = date(2023, 5, 31)


def resolve_pdf_bytes(notefile: NoteFile) -> bytes:
    """Devuelve los bytes del PDF de un ``NoteFile``.

    En local los archivos legados no están en disco: se descargan de S3
    concatenando ``LEGACY_FILES_BASE_URL`` (incluye el prefijo
    ``data_files``) con ``file.name`` (``note_file/<pk>/<archivo>``).
    En producción se leen del storage de Django (S3 con USE_S3_FILES).
    """
    if settings.IS_LOCAL:
        base = settings.LEGACY_FILES_BASE_URL.rstrip("/")
        url = f"{base}/{notefile.file.name}"
        resp = requests.get(
            url, headers=REQUESTS_DEFAULT_HEADERS, timeout=60)
        resp.raise_for_status()
        return resp.content

    notefile.file.open("rb")
    try:
        return notefile.file.read()
    finally:
        notefile.file.close()


def _block_text(block: dict) -> str:
    """Une las líneas/spans de un bloque de texto de PyMuPDF."""
    lines = []
    for line in block.get("lines", []):
        spans = [s.get("text", "") for s in line.get("spans", [])]
        line_text = "".join(spans).strip()
        if line_text:
            lines.append(line_text)
    return "\n".join(lines)


def extract_blocks(pdf_bytes: bytes) -> list[dict]:
    """Extrae bloques de texto con sus coordenadas.

    Cada bloque: ``{"page": int, "bbox": [x0,y0,x1,y1], "text": str}``.
    El ``bbox`` se le pasa a Gemini para distinguir cuerpo de
    cintillos/folios/pies. Se ignoran los bloques de imagen.
    """
    blocks: list[dict] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_index, page in enumerate(doc):
            data = page.get_text("dict")
            for block in data.get("blocks", []):
                if block.get("type") != 0:  # 0 = texto, 1 = imagen
                    continue
                text = _block_text(block).strip()
                if not text:
                    continue
                bbox = [round(c, 1) for c in block.get("bbox", [])]
                blocks.append({
                    "page": page_index + 1,
                    "bbox": bbox,
                    "text": text,
                })
    return blocks


def alnum_char_count(blocks: list[dict]) -> int:
    """Cuenta caracteres alfanuméricos (compuerta MIN_TEXT_CHARS)."""
    return sum(
        sum(1 for ch in block["text"] if ch.isalnum())
        for block in blocks
    )


def article_has_content(article: Article) -> bool:
    """¿El Article tiene contenido real para el pipeline IA?

    ``paragraphs``/``images`` (JSONField) pueden venir como ``None`` o
    como lista vacía ``[]``; ambos casos cuentan como SIN contenido
    (``bool([])`` y ``bool(None)`` son ``False``). Mismo criterio que
    ``reclassify_legal`` a nivel SQL (``exclude(paragraphs=[])``).
    """
    return bool(article.paragraphs) or bool(article.images)


def get_synthetic_scraped_record(source: Source) -> ScrapedRecord:
    """ScrapedRecord sintético reutilizado por fuente.

    Resuelve el FK ``Article.scraped`` (NOT NULL) sin migración.
    Idempotente: una sola fila por fuente.
    """
    record, _ = ScrapedRecord.objects.get_or_create(
        source=source,
        from_date=LEGACY_FROM_DATE,
        to_date=LEGACY_TO_DATE,
        defaults={"status": "completed"},
    )
    return record