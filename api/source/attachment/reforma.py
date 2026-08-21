"""Adjunto de Reforma: la página impresa real, recortada al artículo."""

import logging

from source.attachment.base import AttachmentGenerator, GeneratedAttachment
from source.attachment.pdf_crop import crop_pdf_to_blocks
from source.scraper.reforma import (
    parse_section_notes, primary_page, section_url)
from source.scraper.scraper_base import fetch, get_content

logger = logging.getLogger(__name__)

# La hemeroteca sirve el PDF por CDN firmado: hay que pedir la URL con
# firma antes de descargar; la URL directa devuelve 403.
CDN_URL = (
    "https://www.reforma.com/edicionimpresa/aplicacionei/webview/"
    "GeneraUrl.aspx/PathCDN")
PDF_URL = "https://hemeroteca.reforma.com/{date}/pdfs/{code}.PDF"

TIMEOUT = 60


class ReformaAttachmentGenerator(AttachmentGenerator):
    """PDF de la página donde salió el artículo, recortado a sus bloques."""

    source_url = "https://www.reforma.com"

    def build(self) -> GeneratedAttachment | None:
        page = self.resolve_page()
        if not page or not page.get("texto"):
            return None

        pdf_bytes = self.download_page_pdf(page["texto"])
        if not pdf_bytes:
            return None

        if blocks := page.get("mapeo"):
            pdf_bytes = crop_pdf_to_blocks(pdf_bytes, blocks)

        return GeneratedAttachment(
            pdf_bytes, f"{page['texto']}.pdf", page_code=page["texto"])

    def resolve_page(self) -> dict | None:
        """Página del artículo con sus bloques mapeo."""
        page = primary_page(self.article.get_meta("paginas"))
        if page:
            return page
        # Los artículos scrapeados antes de task-41 no guardaron ni el pag
        # padre ni los mapeo: se recuperan releyendo el XML de la sección.
        return self.resolve_page_from_section()

    def resolve_page_from_section(self) -> dict | None:
        directorio = self.article.get_meta("directorio")
        published_date = self.article.published_date
        if not directorio or not published_date:
            return None

        url = section_url(published_date.strftime("%Y%m%d"), directorio)
        soup = get_content(url, parser="xml", with_proxy=True)
        folio = str(self.article.uid).split("/")[-1]
        note_data = parse_section_notes(soup).get(folio)
        if not note_data:
            return None
        return primary_page(note_data["paginas"])

    def download_page_pdf(self, page_code: str) -> bytes | None:
        published_date = self.article.published_date
        if not published_date:
            return None

        source_url = PDF_URL.format(
            date=published_date.strftime("%Y%m%d"), code=page_code)
        signed_url = self.get_signed_url(source_url)
        if not signed_url:
            return None

        # Misma maquinaria que el scraper: sin fingerprint de Chrome y sin
        # proxy, la hemeroteca responde 403 a la IP del EC2.
        response = fetch(signed_url, with_proxy=True, timeout=TIMEOUT)
        if response is None or response.status_code != 200:
            logger.warning(
                "PDF de Reforma inaccesible (status %s) en %s",
                getattr(response, "status_code", None), signed_url)
            return None
        return response.content

    @staticmethod
    def get_signed_url(source_url: str) -> str | None:
        response = fetch(
            CDN_URL, with_proxy=True, method="post",
            json={"Url": source_url}, timeout=TIMEOUT)
        if response is None or response.status_code != 200:
            logger.warning(
                "Reforma negó la firma CDN (status %s) para %s",
                getattr(response, "status_code", None), source_url)
            return None
        try:
            return response.json().get("d")
        except ValueError:
            logger.warning(
                "Firma CDN de Reforma sin JSON válido para %s", source_url)
            return None
