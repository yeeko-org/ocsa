"""Adjunto de Reforma: la página impresa real, recortada al artículo."""

import requests

from source.attachment.base import AttachmentGenerator, GeneratedAttachment
from source.attachment.pdf_crop import crop_pdf_to_blocks
from source.scraper.reforma import (
    parse_section_notes, primary_page, section_url)
from source.scraper.scraper_base import get_content

# La hemeroteca sirve el PDF por CDN firmado: hay que pedir la URL con
# firma antes de descargar; la URL directa devuelve 403.
CDN_URL = (
    "https://www.reforma.com/edicionimpresa/aplicacionei/webview/"
    "GeneraUrl.aspx/PathCDN")
PDF_URL = "https://hemeroteca.reforma.com/{date}/pdfs/{code}.PDF"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"),
}

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

        response = requests.get(
            signed_url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code != 200:
            return None
        return response.content

    @staticmethod
    def get_signed_url(source_url: str) -> str | None:
        response = requests.post(
            CDN_URL, json={"Url": source_url}, headers=HEADERS,
            timeout=TIMEOUT)
        if response.status_code != 200:
            return None
        try:
            return response.json().get("d")
        except ValueError:
            return None
