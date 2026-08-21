"""Piezas comunes a los dos caminos de contenido de La Jornada."""

import re
from datetime import date
from urllib.parse import urljoin, urlparse

from source.attachment.jornada_media import (
    SITE_ROOT, local_asset, remote_image)
from source.models import Article

MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
    "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

WEEKDAYS = [
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado",
    "Domingo",
]

DEFAULT_SLUG = "politica"

OPENING_CHARS = "([{«“‘¿¡"
CLOSING_CHARS = ")]}»”’,.;:!?…"

# Las imágenes del propio sitio (banderillas, viñetas) viven bajo esta
# ruta; todo lo demás en el marcado es foto del artículo.
STATIC_PATH_PREFIX = "/005/"


def section_slug(article: Article) -> str:
    """Slug de sección tal como lo usa el sitio (.../<fecha>/<slug>/<uid>)."""
    match = re.search(r"/\d{4}/\d{2}/\d{2}/([a-z]+)/", article.url or "")
    return match.group(1) if match else DEFAULT_SLUG


def is_opinion(article: Article) -> bool:
    """Las notas de opinión llevan otro titular, otro crédito y capitular."""
    return (section_slug(article) == "opinion"
            or (article.section or "") == "Opinión")


def spanish_long_date(value: date) -> str:
    return (f"{WEEKDAYS[value.weekday()]} {value.day} de "
            f"{MONTHS[value.month - 1]} de {value.year}")


def page_from_uid(article: Article) -> str | None:
    """Página impresa que codifica el uid de la URL: «031n1est» → 31.

    ``Article.pages`` viene vacío en todo el acervo de La Jornada, pero el
    uid lleva el número; el suplemento de cultura lo prefija con letra
    («a04»). Verificado contra el bloque hemerográfico de 3 000 notas con
    HTML íntegro.
    """
    uid = (article.url or "").rstrip("/").rsplit("/", 1)[-1]
    match = re.match(r"[a-z]?(\d+)", uid)
    return str(int(match.group(1))) if match else None


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def norm(text: str | None) -> str:
    """Normaliza el espaciado de un campo de texto plano.

    Los campos vienen del mismo ``get_text()`` que separa con espacios
    cada etiqueta en línea, así que heredan huecos que en el HTML original
    iban pegados: «( https://… )».
    """
    text = re.sub(r"\s+", " ", (text or "")).strip()
    text = re.sub(r"([%s]) " % re.escape(OPENING_CHARS), r"\1", text)
    return re.sub(r" ([%s])" % re.escape(CLOSING_CHARS), r"\1", text)


def image_source(article: Article, src: str) -> str | None:
    """Resuelve un ``src`` del sitio a data URI, o None si no se pudo.

    Los estáticos salen del repo; las fotos del artículo, de la red.
    """
    if not src:
        return None
    url = urljoin(article.url or SITE_ROOT, src)
    path = urlparse(url).path
    if path.startswith(STATIC_PATH_PREFIX):
        return local_asset(path.rsplit("/", 1)[-1])
    return remote_image(url)
