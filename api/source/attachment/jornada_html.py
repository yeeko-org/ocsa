"""Camino HTML: usa el marcado que el scraper guardó, ya limpio.

Es el camino fiel —conserva cursivas, enlaces y la línea de crédito tipo
«Corresponsal»—, pero solo lo tiene el 12.7% de los artículos: el resto
guardó un cascarón ``<article><!-- DISQUS --></article>``.
"""

from bs4 import BeautifulSoup, NavigableString, Tag

from source.attachment.jornada_content import (
    OPENING_CHARS, CLOSING_CHARS, image_source, page_from_uid,
    spanish_long_date)
from source.models import Article

# Debajo de esto lo guardado es el cascarón, no la nota.
MIN_USABLE_TEXT = 200

# El HTML guardado trae navegación y widgets del sitio; el propio print
# stylesheet de La Jornada los oculta con estas clases.
DROP_CLASSES = ["go", "gui", "penta", "noprint", "iab"]
DROP_IDS = ["comentarios", "disqus_thread", "oasbanner"]

# El scraper guarda el HTML pasado por prettify(), que mete saltos de
# línea alrededor de cada etiqueta en línea; al colapsarlos el render abre
# huecos donde el original iba pegado: «( https://... )».
INLINE_TAGS = ["a", "em", "i", "b", "strong", "span", "q", "sup", "sub",
               "br"]
# Bloques alineados a la derecha o centrados: ahí el espacio sobrante de
# prettify() sí corre el texto, porque no cae al inicio de línea.
TRIMMED_BLOCKS = ["cabeza", "credito-autor", "credito-articulo",
                  "credito-titulo", "hemero", "inicial"]


def has_usable_html(article: Article) -> bool:
    """¿El html_content guardado trae la nota o solo el cascarón?"""
    html = article.html_content or ""
    if len(html) < MIN_USABLE_TEXT:
        return False
    soup = BeautifulSoup(html, "html.parser")
    return len(soup.get_text(strip=True)) >= MIN_USABLE_TEXT


def trim_edges(node: Tag) -> None:
    """Recorta el espacio que prettify() dejó al abrir y cerrar el nodo."""
    strings = node.find_all(string=True)
    if not strings:
        return
    strings[0].replace_with(NavigableString(strings[0].lstrip()))
    # Un nodo solo-espacios queda vacío tras el lstrip y BeautifulSoup
    # lo descarta: la relectura puede volver sin elementos.
    strings = node.find_all(string=True)
    if not strings:
        return
    strings[-1].replace_with(NavigableString(strings[-1].rstrip()))


def tighten_inline(soup: BeautifulSoup) -> None:
    """Quita el espaciado que prettify() dejó junto a etiquetas en línea."""
    for tag in soup.find_all(INLINE_TAGS):
        trim_edges(tag)
        prev, nxt = tag.previous_sibling, tag.next_sibling
        if tag.name == "br":
            if isinstance(prev, NavigableString):
                prev.replace_with(NavigableString(prev.rstrip()))
            if isinstance(nxt, NavigableString):
                nxt.replace_with(NavigableString(nxt.lstrip()))
            continue
        if isinstance(prev, NavigableString) and prev.strip():
            if prev.rstrip()[-1:] in OPENING_CHARS:
                prev.replace_with(NavigableString(prev.rstrip()))
        if isinstance(nxt, NavigableString) and nxt.strip():
            if nxt.lstrip()[:1] in CLOSING_CHARS:
                nxt.replace_with(NavigableString(nxt.lstrip()))


def resolve_images(soup: BeautifulSoup, article: Article) -> None:
    for img in soup.find_all("img", src=True):
        src = image_source(article, img["src"])
        if src:
            img["src"] = src
        else:
            img.decompose()


def add_hemero(soup: BeautifulSoup, body: Tag, article: Article) -> None:
    """Repone el crédito hemerográfico cuando el scraper no lo conservó.

    Es la línea que las editoras usan para citar (día y página). Solo va
    en notas informativas: las de opinión nunca lo llevan.
    """
    is_news = bool(body.find("div", class_="credito-autor"))
    if not is_news or body.find("div", class_="hemero"):
        return
    if not article.published_date:
        return
    holder = body.find("div", class_="col1") or body
    hemero = soup.new_tag("div", attrs={"class": "hemero"})
    page = page_from_uid(article)
    tail = f", p. {page}" if page else ""
    hemero.string = (f"Periódico La Jornada "
                     f"{spanish_long_date(article.published_date)}{tail}")
    holder.insert(0, hemero)


def build_body(article: Article) -> str:
    """Deja el <article> con lo que el print stylesheet del sitio conserva."""
    soup = BeautifulSoup(article.html_content or "", "html.parser")
    for name in DROP_CLASSES:
        for node in soup.find_all(class_=name):
            node.decompose()
    for name in DROP_IDS:
        for node in soup.find_all(id=name):
            node.decompose()
    for anchor in soup.find_all("a"):
        if not anchor.get_text(strip=True):
            anchor.decompose()
    resolve_images(soup, article)
    tighten_inline(soup)
    # prettify() dejó un salto de línea al abrir cada <p> de sumario; ese
    # espacio corre el texto tras la banderilla y adelanta el corte de
    # línea respecto del PDF manual.
    for node in soup.select(".sumarios p"):
        trim_edges(node)
    for name in TRIMMED_BLOCKS:
        for node in soup.find_all(class_=name):
            trim_edges(node)
    body = soup.find("article") or soup
    add_hemero(soup, body, article)
    return str(body)
