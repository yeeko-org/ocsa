"""Plantilla y hoja de estilo del PDF de La Jornada.

Reproduce lo que Chrome imprime desde la página del artículo —que es como
el equipo produce hoy los PDF a mano—: la hoja está transcrita del
site_v7.0.css real, incluidos sus @media print, y la cabecera y el pie de
página imitan los que Chrome añade en el margen.
"""

from django.utils import timezone

from source.attachment.jornada_content import esc, section_slug
from source.attachment.jornada_media import local_asset
from source.models import Article

STYLESHEET = """
@page {
  size: Letter;
  margin: 28.5pt;
  /* Cabecera y pie que Chrome imprime en el margen: fecha de impresión,
     título del documento, URL y folio. */
  @top-left { content: string(printed-at); font: 8pt "Liberation Sans";
              vertical-align: bottom; padding-bottom: 4pt; }
  @top-center { content: string(doc-title); font: 8pt "Liberation Sans";
                vertical-align: bottom; padding-bottom: 4pt;
                white-space: nowrap; }
  @bottom-left { content: string(doc-url); font: 8pt "Liberation Sans";
                 vertical-align: top; padding-top: 4pt; }
  @bottom-right { content: counter(page) "/" counter(pages);
                  font: 8pt "Liberation Sans"; vertical-align: top;
                  padding-top: 4pt; }
}

html { font-size: 16px; }
body {
  margin: 0; padding: 0;
  font-family: "Liberation Serif", Times, "Times New Roman", serif;
  font-size: 16px;
}

/* Los strings viajan al margen desde nodos ocultos del documento. */
.meta-printed-at { string-set: printed-at content(); }
.meta-title { string-set: doc-title content(); }
.meta-url { string-set: doc-url content(); }
.meta { position: absolute; visibility: hidden; height: 0; }

/* Pleca: lo que asoma de la sombra del contenedor blanco del sitio cuando
   Chrome imprime con «Gráficos de fondo». Ocupa los 10px que antes daba el
   margen superior del encabezado, así que no corre nada hacia abajo.
   Medida sobre los PDF manuales: 7.5pt de alto, del blanco al #d2d2d2,
   con las esquinas aclarándose por el desenfoque. */
.page-shadow {
  height: 10px;
  background:
    linear-gradient(to right, rgba(255,255,255,0.55),
                    rgba(255,255,255,0) 4%, rgba(255,255,255,0) 96%,
                    rgba(255,255,255,0.55)),
    linear-gradient(to bottom, #ececec, #d2d2d2);
}

.top-heading { height: 106px; }
.top-heading .heading { position: relative; top: 16px; }
.top-heading .icon { float: left; width: 42px; height: 42px; }
.top-heading .title { float: left; height: 42px; padding-left: 8px; }
.top-heading .logo { float: right; height: 34px; }
.main-toolbar { float: right; margin-top: 7px; margin-right: 5px;
                height: 22px; }
.main-toolbar img { width: 22px; padding-right: 4px; }

/* Hueco que el anuncio lateral deja en la impresión manual del equipo.
   El ancho es el del banner real (300px, el «medium rectangle» de IAB).
   El alto NO es el del anuncio (250px): en la página viva el bloque de la
   foto ignora el flotante, así que 115px es el valor que reproduce los
   cortes de línea de los cuatro PDF manuales —cualquier valor entre 105 y
   120 da el mismo resultado en los cuatro. */
.ad-gap { float: right; width: 300px; height: 115px; }

/* En impresión el sitio suelta las dos columnas a un solo hilo. */
.main-cont.article-cont { width: 522px; margin: 0 auto; }
.article-cont .text .col1, .article-cont .text .col2 {
  float: none; width: auto; }

.article-cont .cabeza { margin: 12px 0; font-weight: bold; font-size: 24px; }
.article-cont.opinion .cabeza, .article-cont.analysis .cabeza {
  text-align: center; line-height: 44px; font-size: 44px; }
.article-cont .sumarios p {
  margin: 0 0 6px 0; font-size: 18px; text-indent: 0; text-align: left; }
.article-cont .sumarios p::before {
  content: url("BULLET_SOL_09"); padding-right: 1ex; }
.article-cont.opinion .sumarios p, .article-cont.analysis .sumarios p {
  text-align: center; }

.article-cont .foto { margin-bottom: 10px; }
.article-cont .foto img { width: 100%; border: 1px solid black; }
.pie-foto { text-align: justify; line-height: 11.5px;
            font-family: "Liberation Sans", Helvetica, Arial, sans-serif;
            font-size: 11px; }
.pie-foto .credito { font-weight: bold; font-size: 11px;
                     white-space: nowrap; }
.pie-foto .credito::before {
  content: url("BULLET_SOL_06"); padding-right: 0.5ex; padding-left: 0.5ex; }

.credito-autor {
  padding-left: 0.6ex; border-bottom: 1px solid #626366;
  border-left: 1ex solid #626366;
  font-family: "Liberation Sans", Arial, sans-serif;
  font-variant: small-caps; font-variant-caps: small-caps;
  font-weight: bold; font-size: 15px; line-height: 15px; margin-top: 10px; }
.credito-articulo {
  text-align: center; text-decoration: underline;
  font-family: "Liberation Sans", Arial, sans-serif;
  font-variant: small-caps; font-variant-caps: small-caps;
  font-size: 15px; line-height: 15px; margin: 20px 0; }
.article-cont .credito-titulo, .article-cont .hemero {
  text-align: right; font-family: "Liberation Sans", Helvetica, sans-serif;
  font-size: 14px; margin-bottom: 8px; }
.article-cont .hemero { font-size: 11px; }

.article-cont .text { margin-top: 12px; }
.article-cont .text p {
  margin: 0 0 16px 0; text-indent: 3ex; text-align: justify; }
.article-cont .text p.s-s, .article-cont .text p.sumario { text-indent: 0; }
/* El sitio solo pone banderilla al sumario intercalado cuando trae clase
   de cuerpo (.sumario.p13 y demás), y el HTML guardado no la conserva. */
.article-cont .text p.sumario { font-weight: bold; text-align: left; }
.article-cont.opinion .text p.sumario,
.article-cont.analysis .text p.sumario { text-align: center; }
.article-cont .text .inicial {
  float: left; font-size: 95px; line-height: 75px; padding-right: 2px; }
.article-cont .text .email { text-align: center; }
.article-cont a { color: #bd2e26; text-decoration: none; }
.article-cont .text p .loc {
  font-family: "Liberation Sans", Helvetica, sans-serif; font-size: 12px;
  font-weight: bold; }

/* La foto y su pie deben viajar juntos: partirlos delata el PDF generado. */
.article-cont .foto { break-inside: avoid; }
"""


def build_stylesheet() -> str:
    """Hoja de estilo con las viñetas ya empotradas."""
    css = STYLESHEET
    for token, name in (("BULLET_SOL_09", "sol-09.png"),
                        ("BULLET_SOL_06", "sol-06.png")):
        css = css.replace(token, local_asset(name) or "")
    return css


def build_heading(article: Article) -> str:
    """Cabecera del sitio: icono y banderilla de la sección, más el logo."""
    slug = section_slug(article)
    images = [
        ("icon", local_asset(f"sect-icn-{slug}-trans.png"), slug),
        ("title", local_asset(f"heading-{slug}-trans.png"), slug),
        ("logo", local_asset("logo_negro.png"), "La Jornada"),
    ]
    tags = "".join(
        f'<img class="{css_class}" src="{src}" alt="{alt}">'
        for css_class, src, alt in images if src)
    rss = local_asset("icn-rss.png")
    toolbar = (f'<div class="main-toolbar"><img src="{rss}" alt="RSS"></div>'
               if rss else "")
    return (f'<div class="top-heading"><div class="heading">{tags}</div>'
            f'</div>{toolbar}')


def build_html(article: Article, body: str, ad_gap: bool = True) -> str:
    """Documento completo listo para WeasyPrint.

    ``ad_gap`` deja el hueco del banner lateral: es lo que sale en la
    impresión manual del equipo, así que va por omisión.
    """
    printed_at = timezone.localtime().strftime("%-d/%-m/%y, %H:%M")
    gap = '<div class="ad-gap"></div>' if ad_gap else ""
    return f"""<!DOCTYPE html>
<html lang="es-MX"><head><meta charset="utf-8">
<style>{build_stylesheet()}</style></head><body>
<div class="meta meta-printed-at">{printed_at}</div>
<div class="meta meta-title">La Jornada: {esc(article.title or '')}</div>
<div class="meta meta-url">{esc(article.url or '')}</div>
<div class="page-shadow"></div>
{build_heading(article)}
{gap}
{body}
</body></html>"""
