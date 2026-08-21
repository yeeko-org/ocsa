"""Recorte de una página de PDF a partir de bloques normalizados."""

import fitz  # PyMuPDF

# Los bloques mapeo se ajustan al texto sin holgura: sin este margen el
# recorte come el borde de titulares y filetes. En puntos PDF (1/72").
CROP_MARGIN_PT = 6.0

# Las fracciones del XML se quedan cortas contra la mancha real del PDF:
# medidas contra el texto en 12 páginas de 4 fechas y 7 secciones, el
# óptimo por página cae entre 1.017 y 1.023 en ambos ejes, sin traslación
# (la arista izquierda ya coincide). El origen del desfase está del lado
# de Reforma —el lienzo donde el CMS mide no es el que declara
# anchojpg/altojpg—, así que esto es calibración empírica, no una
# conversión de unidades.
MAPEO_SCALE = 1.019

# Umbral para dar dos bloques por vecinos. En las 12 páginas medidas, la
# separación máxima dentro de un mismo artículo es de 31 pt (un titular
# despegado de su cuerpo) y la única pieza realmente ajena está a 685 pt:
# el valle es enorme y el umbral se pone lejos del máximo interno, porque
# partir de más un artículo le corta contenido y unir de más solo repite
# lo que ya hacía el recorte anterior.
BLOCK_GAP_PT = 72.0


def blocks_to_rects(
        blocks: list[dict], page_rect: "fitz.Rect") -> list["fitz.Rect"]:
    """Pasa los bloques del XML a rectángulos de la página.

    Cada bloque trae ``x``/``y``/``width``/``height`` como fracciones de
    0 a 1 del ancho y alto de la página, con origen en la esquina
    superior izquierda —el mismo sentido del eje Y que usa PyMuPDF—, así
    que basta escalarlas por el tamaño de la página y por ``MAPEO_SCALE``.
    """
    width = page_rect.width * MAPEO_SCALE
    height = page_rect.height * MAPEO_SCALE
    return [
        fitz.Rect(
            b["x"] * width, b["y"] * height,
            (b["x"] + b["width"]) * width, (b["y"] + b["height"]) * height)
        for b in blocks if b.get("width") and b.get("height")
    ]


def largest_component(
        rects: list["fitz.Rect"], gap: float = BLOCK_GAP_PT
) -> list["fitz.Rect"]:
    """Bloques del grupo con más superficie entre los que se tocan.

    Un folio puede cargar dos piezas visualmente disjuntas —el artículo y
    un recuadro ajeno en otra esquina—; su caja envolvente se comería
    media plana. Se agrupan los bloques que se tocan o casi (``gap``) y
    se conserva solo el grupo de mayor área.
    """
    parent = list(range(len(rects)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    grown = [fitz.Rect(r) + (-gap / 2, -gap / 2, gap / 2, gap / 2)
             for r in rects]
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if not (grown[i] & grown[j]).is_empty:
                parent[find(i)] = find(j)

    groups: dict[int, list["fitz.Rect"]] = {}
    for index, rect in enumerate(rects):
        groups.setdefault(find(index), []).append(rect)
    return max(
        groups.values(),
        key=lambda group: sum(r.get_area() for r in group))


def blocks_to_rect(
        blocks: list[dict], page_rect: "fitz.Rect") -> "fitz.Rect | None":
    """Rectángulo del artículo: envolvente de su componente principal."""
    rects = blocks_to_rects(blocks, page_rect)
    if not rects:
        return None

    rect = fitz.Rect()
    for block_rect in largest_component(rects):
        rect |= block_rect
    rect &= page_rect
    return rect if not rect.is_empty else None


def expand_to_page_content(page: "fitz.Page", rect: "fitz.Rect") -> "fitz.Rect":
    """Estira el rectángulo hasta cubrir entero lo que ya contiene.

    Los mapeo describen las cajas del CMS, no la mancha impresa: una
    columna justificada puede rebasarlas por varios puntos y el recorte
    saldría con el texto cortado. Se anexa cada bloque cuyo centro cae
    dentro del rectángulo; exigir el centro —y no el mero traslape— evita
    arrastrar la columna del artículo vecino.
    """
    expanded = fitz.Rect(rect)
    for block in page.get_text("blocks"):
        block_rect = fitz.Rect(block[:4])
        if rect.contains((block_rect.tl + block_rect.br) / 2):
            expanded |= block_rect
    return expanded


def crop_pdf_to_blocks(
        pdf_bytes: bytes, blocks: list[dict], page_index: int = 0) -> bytes:
    """Recorta la página a la unión de los bloques del artículo.

    Devuelve el PDF original si los bloques no delimitan nada usable.
    """
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        page = doc[page_index]
        rect = blocks_to_rect(blocks, page.rect)
        if rect is None:
            return pdf_bytes
        rect = expand_to_page_content(page, rect)
        rect += (
            -CROP_MARGIN_PT, -CROP_MARGIN_PT, CROP_MARGIN_PT, CROP_MARGIN_PT)
        rect &= page.rect
        # Recortar por cropbox conserva el vectorial de la página; el
        # contenido fuera del recorte sigue en el archivo pero no se ve.
        page.set_cropbox(rect)
        return doc.tobytes()
