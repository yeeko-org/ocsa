from pprint import pprint
import re

from datetime import date

from bs4 import BeautifulSoup
from bs4.element import Tag

from source.models import ScrapedRecord, Source
from profile_auth.models import User
from source.scraper.articles import (
    ArticleScraper, MainScraper, ManagerScraper)
from source.scraper.scraper_base import (
    get_content, get_clean_text, ScraperSession)


MAIN_URL = (
    "https://www.reforma.com/edicionimpresa/aplicacionei/webview/ws/"
    "wsEdImpresa.asmx/LeerXML?strName=https://hemerotecalibre.reforma.com/")

IGNORE_SECTIONS = [
    "avisos",
    "cancha",
    "gente",
    "cultura",
    "vida",
    "revistar",
    "deviaje",
    "automotriz",
    "moda",
    "buenamesa",
    "primerafila",
    "club",
    "campanas",
    "gadgets",
    "bienesraices",
    "blindajeautomotriz",
    "entremuros",
    "primariasbasessolidas",
    "edomex",
    "supertazonlix",
    "proveedoresdelaindustriarestaurantera",
    "podiumespecial",
    "efponteenforma",
    "posgrados",
    "universitarios",
    "clubanuario",
    "adjudicadoshir",
    "prevencionessalud",
    "centenarius",
    "gadgetslarevista",
    "podium",
]


def section_url(scraper_date: str, directorio: str) -> str:
    """URL del XML de una sección (jerárquico: pag > notas > nota)."""
    return f"{MAIN_URL}{scraper_date}/secciones/{directorio.upper()}.XML"


def parse_mapeo_blocks(nota: Tag) -> list[dict]:
    """Bloques del artículo sobre la página impresa.

    mapeoX/Y/Width/Height vienen como fracciones de 0 a 1 del ancho y
    alto de la página, con origen en la esquina superior izquierda.
    """
    blocks = []
    for mapeo in nota.find_all("mapeo"):
        block = {}
        for key, tag_name in (
                ("x", "mapeoX"), ("y", "mapeoY"),
                ("width", "mapeoWidth"), ("height", "mapeoHeight")):
            tag = mapeo.find(tag_name)
            try:
                block[key] = float(tag.text)
            except (AttributeError, TypeError, ValueError):
                block = {}
                break
        if block:
            blocks.append(block)
    return blocks


def parse_section_notes(soup: BeautifulSoup) -> dict[str, dict]:
    """Agrupa las notas del XML de sección por folio.

    Cada folio devuelve ``{"attrs": dict, "paginas": [...]}``, donde
    cada página trae ``numero``, ``texto`` (el código de la página, el
    mismo que usa la URL del PDF en hemeroteca) y sus bloques ``mapeo``.
    Un folio puede aparecer en varias páginas (pases) y varias veces
    dentro de la misma página.
    """
    notes: dict[str, dict] = {}

    for pag in soup.find_all("pag"):
        code = pag.get("nombre")
        if not code:
            continue
        for nota in pag.find_all("nota"):
            folio = str(nota.get("folio") or "")
            if not folio or folio == "0":
                continue
            entry = notes.setdefault(
                folio, {"attrs": dict(nota.attrs), "paginas": []})
            page = next(
                (p for p in entry["paginas"] if p["texto"] == code), None)
            if page is None:
                page = {
                    "numero": pag.get("num"), "texto": code, "mapeo": []}
                entry["paginas"].append(page)
            page["mapeo"].extend(parse_mapeo_blocks(nota))

    return notes


def primary_page(paginas: list[dict] | None) -> dict | None:
    """Página donde el artículo ocupa más superficie.

    Los pases a otras páginas aportan bloques menores que el arranque,
    así que la mayor área es la página que representa al artículo.
    """
    if not paginas:
        return None
    return max(
        paginas,
        key=lambda page: sum(
            block["width"] * block["height"]
            for block in page.get("mapeo", [])
        )
    )


class ReformaManagerScraper(ManagerScraper):

    date_format = "%Y%m%d"

    def __init__(
            self, from_date: str | date | None, to_date: str | date | None,
            recover_record: ScrapedRecord | None = None,
            user: User | None = None
    ) -> None:
        super().__init__(
            from_date, to_date,
            main_scraper_class=ReformaMainScraper,
            article_scraper_class=ReformaArticleScraper,
            recover_record=recover_record,
            user=user
        )

    def get_source(self) -> Source:
        if not hasattr(self, "_source"):
            self.source, _ = Source.objects.get_or_create(
                main_url="https://www.reforma.com", defaults={
                    "name": "El Reforma",
                    "is_news": True
                })
        return self.source


class ReformaMainScraper(MainScraper):

    need_proxy = True
    parser = "xml"
    date_format = "%Y%m%d"

    def __init__(
            self, scraper_date: date | str,
            session: ScraperSession | None = None):
        self.parser = "xml"
        self.scraper_date = self.date_in_str(scraper_date)
        self.soup_content = get_content(
            self.main_url(), self.parser, self.need_proxy, session=session)
        print("main url", self.main_url())
        print("scraping date", self.scraper_date)
        super().__init__(scraper_date, session=session)

        for _, section_data in self.sections_dict.items():
            if "articles" not in section_data:
                continue
            for article in section_data["articles"]:
                article["uid"] = f"{scraper_date}/{article.get('uid')}"

    def main_url(self):
        return f"{MAIN_URL}{self.scraper_date}/PORTADAS.XML"

    def get_sections(self):
        self.sections_dict = {}

        for seccion in self.soup_content.find_all("seccion"):
            if str(seccion.get("fechapub")) != self.scraper_date:
                continue
            if directorio := seccion.get("directorio"):
                if str(directorio).lower() in IGNORE_SECTIONS:
                    continue
                directorio = str(directorio).upper()
            else:
                continue

            nombre = seccion.get("nombre")
            id_seccion = seccion.get("idseccion")
            paginas = [
                {"numero": pagina.get("numero"), "texto": pagina.text}
                for pagina in seccion.find_all("pagina")
            ]

            self.sections_dict[directorio] = {
                "nombre": nombre,
                "directorio": directorio,
                "id_seccion": id_seccion,
                "portada": paginas[0] if paginas else None,
                "url": section_url(self.scraper_date, directorio)
            }

    def get_articles(self):
        for _, section_data in self.sections_dict.items():
            section_url = section_data["url"]
            try:
                section_data["articles"] = ReformaSectionScraper(
                    section_url, meta_section={
                        "nombre": section_data["nombre"],
                        "directorio": section_data["directorio"],
                        "id_seccion": section_data["id_seccion"],
                        "portada": section_data["portada"],
                    }, session=self.session).articles
            except Exception as e:
                section_data["error"] = str(e)
                continue
            if not section_data["articles"]:
                # Sin error pero sin artículos: casi siempre es el selector
                # que dejó de coincidir, no una sección vacía de verdad.
                section_data["empty"] = True


class ReformaSectionScraper:
    soup_content: BeautifulSoup
    articles: list[dict]
    meta_section: dict

    def __init__(
            self, url: str, meta_section: dict | None = None,
            session: ScraperSession | None = None):
        self.meta_section = meta_section or {}
        self.soup_content = get_content(
            url, parser="xml", with_proxy=True, session=session)
        self.get_articles()

    def get_articles(self):

        self.articles = []

        for uid, note_data in parse_section_notes(self.soup_content).items():
            attrs = note_data["attrs"]
            url = (
                "https://www.reforma.com/edicionimpresa/aplicacionEI/webview/"
                f"iWebView.aspx?Coleccion=1066&Folio={uid}&TipoTrans=8"
            )
            metadata = {
                key: attrs.get(key) for key in (
                    "idcoleccion", "paginacms", "grupocms", "ideditorial",
                    "cms")
            }
            metadata.update(self.meta_section)
            metadata["paginas"] = note_data["paginas"]
            if page := primary_page(note_data["paginas"]):
                metadata["pagina"] = {
                    "numero": page["numero"], "texto": page["texto"]}
                metadata["mapeo"] = page["mapeo"]
            self.articles.append({
                "uid": uid,
                "metadata": metadata,
                "url": url
            })


class ReformaArticleScraper(ArticleScraper):
    need_proxy = True

    def get_article_data(self):
        self.title = ""
        self.subtitle = ""
        self.content = ""
        self.images = []
        self.author = ""

        try:
            self.get_article_data_script_var()
        except Exception as e:
            print(f"Error getting article data script var: {e}")

        try:
            wrapper = self.get_main_body()
        except Exception as e:
            print(f"Error getting main body: {e}")
            raise e

        if not wrapper:
            return

        if not self.author:
            author_div = wrapper.find("div", class_="autor")
            if author_div:
                self.author = get_clean_text(author_div)
        if not self.title:
            title_div = wrapper.find("div", class_="titulo")
            if title_div:
                self.title = get_clean_text(title_div)
        if not self.subtitle:
            # Try to find subtitle in a div without class and with some content
            subtitle_div = wrapper.find("div", class_=lambda x: not x and x)
            if subtitle_div:
                self.subtitle = get_clean_text(subtitle_div)

        content_div = wrapper.find("div", id="divImgPagina")
        if not content_div:
            return

        try:
            self.content = "\n\n".join(
                p.get_text() for p in content_div.find_all("p")
                if p.get_text(strip=True) and p.get_text(strip=True) != " "
            ).strip()
        except Exception as e:
            print(f"Error getting content: {e}")
            raise e
        # <div id="divTituloNota" class="titulo">
        # <div id="divTextoNota" class="texto">
        try:
            if not self.title:
                title_div = content_div.find("div", id="divTituloNota")
                if title_div:
                    self.title = get_clean_text(title_div)
            if not self.subtitle:
                subtitle_div = content_div.find("div", id="divTextoNota")
                if subtitle_div:
                    self.subtitle = get_clean_text(subtitle_div)

            self.images = [
                {"src": img["src"], "caption": img.get("alt", "")}
                for img in content_div.find_all("img")
                if img.get("src")
            ]

            if not self.title and self.subtitle:
                self.title = self.subtitle[:250]
                if len(self.subtitle) > 250:
                    self.title += "..."
        except Exception as e:
            print(f"Error processing content: {e}")
            raise e

    def get_main_body(self) -> Tag:
        return self.soup_content.find("div", id="wrapper")

    def special_cleanup(self, body):
        # Decompose <a> with id = "page_link_prev" and "page_link_next"
        classes_to_remove = []
        for a in body.find_all('div', class_=classes_to_remove):
            a.decompose()

        return body

    def get_article_data_script_var(self):

        # body = self.soup_content.find("body")
        if not (body := self.soup_content.find("body")):
            return
        # scripts_inside_body = body.find_all("script")
        if not (scripts_inside_body := body.find_all("script")):
            return

        script_contents = [
            script.string for script in scripts_inside_body if script.string]

        all_content = "".join(script_contents)
        lines = re.findall(r'.+', all_content)

        # data = {match[1].strip(): match[2].strip()
        #         for match in pattern.finditer(all_content)}
        pattern = re.compile(
            r"[\s{3,}]var (\w+)=['\"]([^;]+)['\"];?$", re.MULTILINE)

        data: dict[str, str] = {}
        for line in lines:
            match = pattern.finditer(line)
            for m in match:
                key = m[1].strip()
                value = m[2].strip()
                data[key] = value

        self.title = data.get("Titulo", None)
        self.subtitle = data.get("Resumen", None)
        self.author = data.get("autor", None)
        # pprint(data)
