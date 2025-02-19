from pprint import pprint
import re

from datetime import date

from bs4 import BeautifulSoup
from bs4.element import Tag

from source.models import ScrapedRecord, Source
from source.scraper.articles import (
    ArticleScraper, MainScraper, ManagerScraper, get_content)

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
                    section_url).articles
            except Exception as e:
                section_data["error"] = str(e)


class ReformaSectionScraper:
    soup_content: BeautifulSoup
    articles: list[dict]

    def __init__(self, url: str):
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

            idcolecion = seccion.get("idcoleccion")
            paginacms = seccion.get("paginacms")
            grupocms = seccion.get("grupocms")
            ideditorial = seccion.get("ideditorial")
            cms = seccion.get("cms")
            url = (
                "https://www.reforma.com/edicionimpresa/aplicacionEI/webview/"
                f"iWebView.aspx?Coleccion=1066&Folio={uid}&TipoTrans=8"
            )
            self.articles.append({
                "uid": uid,
                "idcoleccion": idcolecion,
                "paginacms": paginacms,
                "grupocms": grupocms,
                "ideditorial": ideditorial,
                "cms": cms,
                "url": url
            })


class ReformaArticleScraper(ArticleScraper):

    def get_article_data(self):
        self.title = ""
        self.subtitle = ""
        self.content = ""
        self.images = []
        self.author = ""

        self.get_article_data_script_var()

        wrapper = self.get_main_body()

        if not wrapper:
            return

        content_div = wrapper.find("div", id="divImgPagina")
        if not content_div:
            return

        self.content = "\n".join(
            p.get_text(strip=True) for p in content_div.find_all("p"))

        self.images = [
            img["src"]
            for img in content_div.find_all("img")
            if img.get("src")
        ]

        if not self.title and self.subtitle:
            self.title = self.subtitle[:250]
            if len(self.subtitle) > 250:
                self.title += "..."

        self.content = "\n".join(
            [self.title, self.subtitle, self.content]).strip()

    def get_main_body(self) -> Tag:
        return self.soup_content.find("div", id="wrapper")

    def get_article_data_script_var(self):

        if not (body := self.soup_content.find("body")):
            return

        if not (scripts_inside_body := body.find_all("script")):
            return

        script_contents = [
            script.string for script in scripts_inside_body if script.string]

        pattern = re.compile(
            r"var (\w+)\s*=\s*['\"]?([^;'\"]+)['\"]?;?", re.MULTILINE)
        data = {match[1].strip(): match[2].strip()
                for match in pattern.finditer("".join(script_contents))}

        self.title = data.get("Titulo", "No encontrado")
        self.subtitle = data.get("Resumen", "")
        self.author = data.get("autor", "No especificado")
        pprint(data)
