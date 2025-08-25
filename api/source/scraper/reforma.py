from pprint import pprint
import re

from datetime import date

from bs4 import BeautifulSoup
from bs4.element import Tag

from source.models import ScrapedRecord, Source
from source.scraper.articles import (
    ArticleScraper, MainScraper, ManagerScraper)
from source.scraper.scraper_base import get_content, get_clean_text


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


class ReformaManagerScraper(ManagerScraper):

    date_format = "%Y%m%d"

    def __init__(
            self, from_date: str | date, to_date: str | date,
            recover_record: ScrapedRecord | None = None,
            open_ai_engine: str | None = None
    ) -> None:
        super().__init__(
            from_date, to_date, ReformaMainScraper, ReformaArticleScraper,
            recover_record=recover_record, open_ai_engine=open_ai_engine
        )

    def get_source(self) -> Source:
        if not hasattr(self, "_source"):
            self._source, _ = Source.objects.get_or_create(
                main_url="https://www.reforma.com", defaults={
                    "name": "El Reforma",
                    "is_news": True
                })
        return self._source


class ReformaMainScraper(MainScraper):
    parser = "xml"

    def __init__(self, scraper_date: date | str):
        super().__init__(scraper_date)

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
                "pagina": paginas[0] if paginas else None,
                "url": f"{MAIN_URL}{self.scraper_date}/secciones/{directorio}.XML"
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
                        "pagina": section_data["pagina"],
                    }).articles
            except Exception as e:
                section_data["error"] = str(e)


class ReformaSectionScraper:
    soup_content: BeautifulSoup
    articles: list[dict]
    meta_section: dict

    def __init__(self, url: str, meta_section: dict | None = None):
        self.meta_section = meta_section or {}
        self.soup_content = get_content(url, parser="xml")
        self.get_articles()

    def get_articles(self):

        self.articles = []

        for seccion in self.soup_content.find_all("nota"):
            # idcoleccion="1066" folio="2504954" paginacms="0" grupocms="0" ideditorial="0" urlanuncio="" cms="1"

            if uid := seccion.get("folio"):
                uid = str(uid)
            else:
                continue
            if uid == "0":
                continue

            idcolecion = seccion.get("idcoleccion")
            paginacms = seccion.get("paginacms")
            grupocms = seccion.get("grupocms")
            ideditorial = seccion.get("ideditorial")
            cms = seccion.get("cms")
            url = (
                "https://www.reforma.com/edicionimpresa/aplicacionEI/webview/"
                f"iWebView.aspx?Coleccion=1066&Folio={uid}&TipoTrans=8"
            )
            metadata = {
                "idcoleccion": idcolecion,
                "paginacms": paginacms,
                "grupocms": grupocms,
                "ideditorial": ideditorial,
                "cms": cms,
            }
            metadata.update(self.meta_section)
            self.articles.append({
                "uid": uid,
                "metadata": metadata,
                "url": url
            })


class ReformaArticleScraper(ArticleScraper):

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
