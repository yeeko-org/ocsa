"""Generadores de adjunto por fuente, análogos a los scrapers.

Proceso queda fuera a propósito: sus adjuntos se cargan a mano.
"""

from source.attachment.base import AttachmentGenerator, GeneratedAttachment
from source.attachment.jornada import JornadaAttachmentGenerator
from source.attachment.reforma import ReformaAttachmentGenerator

GENERATORS: tuple[type[AttachmentGenerator], ...] = (
    JornadaAttachmentGenerator,
    ReformaAttachmentGenerator,
)

__all__ = [
    "AttachmentGenerator",
    "GeneratedAttachment",
    "JornadaAttachmentGenerator",
    "ReformaAttachmentGenerator",
    "get_attachment_generator",
    "generate_attachment",
]


def get_attachment_generator(source) -> "type[AttachmentGenerator] | None":
    """Generador registrado para la fuente, si lo hay."""
    main_url = (getattr(source, "main_url", "") or "").rstrip("/").lower()
    if not main_url:
        return None
    for generator in GENERATORS:
        if generator.source_url.rstrip("/").lower() == main_url:
            return generator
    return None


def generate_attachment(article, note=None, replace: bool = False):
    """Genera el adjunto del artículo si su fuente tiene generador.

    Punto de entrada único: lo usa la creación de la nota y también la
    regeneración masiva sobre notas ya existentes (``note`` explícita).
    """
    generator_class = get_attachment_generator(article.source)
    if not generator_class:
        return None
    return generator_class(article).generate(note=note, replace=replace)
