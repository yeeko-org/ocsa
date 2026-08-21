"""Camino de campos: reconstruye el marcado del sitio sin HTML guardado.

Solo el 12.7% de los artículos conserva ``html_content``; el resto guarda
un cascarón vacío. Con title, subtitle, paragraphs, author, images, url y
published_date se rearma el mismo árbol contra el que está escrita la
hoja de estilo (div.cabeza, .sumarios, .foto, .credito-autor, .hemero).
Lo único irrecuperable es la línea de crédito tipo «Corresponsal», que se
omite.
"""

import re

from source.attachment.jornada_content import (
    esc, image_source, is_opinion, norm, page_from_uid, spanish_long_date)
from source.models import Article

# Umbral medido sobre 933 notas de un solo sumario con HTML íntegro: por
# debajo de 49 caracteres el sumario va ARRIBA del titular (antetítulo) y
# por encima va abajo (bajada). Acierta en 88.5% de los casos; con dos o
# más sumarios el orden de `subtitle` ya resuelve la posición.
KICKER_MAX_LEN = 49

CREDIT_RE = re.compile(r"(?<=\S)(Foto\s.+)$")


def split_sumarios(article: Article) -> tuple[list[str], list[str]]:
    """Reparte los sumarios entre antetítulo (arriba) y bajada (abajo).

    ``subtitle`` los guarda en orden de documento separados por salto de
    línea, pero perdió su posición respecto al titular.
    """
    parts = [norm(p) for p in (article.subtitle or "").split("\n")]
    parts = [p for p in parts if p]
    if not parts:
        return [], []
    if len(parts) == 1:
        return (parts, []) if len(parts[0]) < KICKER_MAX_LEN else ([], parts)
    return parts[:1], parts[1:]


def split_caption(caption: str) -> tuple[str, str]:
    """Separa el pie de foto de su crédito («…en 2014.Foto Cristina Gómez»).

    El scraper concatena sin espacio el texto del pie con el
    ``<span class="credito">`` que lo cierra, así que el punto final marca
    la costura.
    """
    text = norm(caption)
    match = CREDIT_RE.search(text)
    if not match:
        return text, ""
    credit = match.group(1)
    # Mismo pegado un nivel adentro: «Especial paraLa Jornada» traía el
    # nombre del diario en <em>.
    credit = re.sub(r"(?<=[a-záéíóúñ])(La Jornada)", r" \1", credit)
    return text[:match.start()].strip(), credit


def sumario_block(items: list[str]) -> str:
    if not items:
        return ""
    inner = "".join(f"<p>{esc(text)}</p>" for text in items)
    return f'<div class="sumarios">{inner}</div>'


def photos_block(article: Article) -> str:
    """Fotos con su pie; las que no se pudieron bajar simplemente no van."""
    html = ""
    for image in (article.images or []):
        src = image_source(article, image.get("src") or "")
        if not src:
            continue
        text, credit = split_caption(image.get("caption") or "")
        credit_html = (f'<span class="credito">{esc(credit)}</span>'
                       if credit else "")
        html += (f'<div class="foto"><img src="{src}" alt="">'
                 f'<div class="pie-foto">{esc(text)} {credit_html}</div>'
                 f'</div>')
    return html


def hemero_block(article: Article) -> str:
    """Crédito hemerográfico: es la línea con que las editoras citan."""
    if not article.published_date:
        return ""
    page = page_from_uid(article)
    tail = f", p. {page}" if page else ""
    return ('<div class="hemero">Periódico La Jornada<br>'
            f'{spanish_long_date(article.published_date)}{tail}</div>')


def body_paragraphs(article: Article, sumarios: set[str]) -> list[str]:
    """Párrafos del cuerpo, sin los sumarios que `paragraphs` repite."""
    paragraphs = [norm(p) for p in (article.paragraphs or [])]
    return [p for p in paragraphs if p and p not in sumarios]


def build_body(article: Article) -> str:
    """Arma el marcado de la nota (div.cabeza, .sumarios, .foto, .text…)."""
    opinion = is_opinion(article)
    kind = "analysis" if opinion else "actuality"
    above, below = split_sumarios(article)
    author = norm(article.author)
    pars = body_paragraphs(article, set(above) | set(below))

    head = ""
    if opinion and author:
        head = (f'<div class="credito-articulo"><span>{esc(author)}</span>'
                f'</div>')

    col = ""
    if not opinion and author:
        col += (f'<div class="credito-autor"><span>{esc(author)}</span>'
                f'</div>')
    if not opinion:
        col += hemero_block(article)

    first, rest = (pars[:1], pars[1:]) if pars else ([], [])
    if first and opinion:
        # Capitular: el sitio saca la primera letra a un div propio.
        col += f'<div class="inicial">{esc(first[0][0])}</div>'
        col += f'<p class="s-s">{esc(first[0][1:])}</p>'
    elif first:
        col += f'<p class="s-s">{esc(first[0])}</p>'
    col += "".join(f"<p>{esc(p)}</p>" for p in rest)

    return (f'<div class="main-cont article-cont {kind}">'
            f'{sumario_block(above)}'
            f'<div class="cabeza">{esc(article.title or "")}</div>'
            f'{sumario_block(below)}'
            f'{head}'
            f'<div class="text">{photos_block(article)}'
            f'<div class="col col1">{col}</div>'
            f'</div></div>')
