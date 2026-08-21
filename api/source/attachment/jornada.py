"""Adjunto de La Jornada: la página del artículo, impresa a PDF.

La Jornada no publica un PDF de la edición impresa, así que el equipo
imprime a mano la página web del artículo desde Chrome. Este generador
reproduce esa impresión sin visitar la nota en vivo, desde lo que el
scraper ya guardó.
"""

from weasyprint import HTML

from source.attachment.base import AttachmentGenerator, GeneratedAttachment
from source.attachment import jornada_fields, jornada_html
from source.attachment.jornada_content import page_from_uid, section_slug
from source.attachment.jornada_render import build_html


class JornadaAttachmentGenerator(AttachmentGenerator):
    """PDF de la página del artículo, con el hueco del banner lateral."""

    source_url = "https://www.jornada.com.mx"

    def build(self) -> GeneratedAttachment | None:
        body = self.build_body()
        if not body:
            return None

        # Un marcado raro o una fuente ausente revientan aquí; los atrapa
        # la red de seguridad de AttachmentGenerator.safe_build.
        document = build_html(self.article, body)
        pdf_bytes = HTML(string=document).write_pdf()
        if not pdf_bytes:
            return None

        page_code = page_from_uid(self.article)
        return GeneratedAttachment(
            pdf_bytes, self.file_name(page_code), page_code=page_code)

    def build_body(self) -> str | None:
        """Cuerpo del artículo por el mejor camino disponible.

        El HTML guardado es el camino fiel (conserva cursivas, enlaces y
        la línea de crédito tipo «Corresponsal»), pero solo lo tiene una
        minoría de los artículos.
        """
        if jornada_html.has_usable_html(self.article):
            return jornada_html.build_body(self.article)
        if not self.article.title or not self.article.paragraphs:
            return None
        return jornada_fields.build_body(self.article)

    def file_name(self, page_code: str | None) -> str:
        """Nombre distinguible del que produce el equipo a mano.

        Los manuales se llaman ``La_Jornada_<sección>.pdf``; el prefijo
        ``LJ_`` más la fecha y la página dejan ver de un vistazo cuáles
        salieron de aquí.
        """
        parts = ["LJ", section_slug(self.article)]
        if self.article.published_date:
            parts.append(self.article.published_date.strftime("%Y%m%d"))
        if page_code:
            parts.append(f"p{page_code}")
        return "_".join(parts) + ".pdf"
