"""
Scraper de Proceso usando la API de PressReader.
Hecho por Martín Szyszlican <martin@abrimos.info>

Este scraper obtiene artículos de la revista Proceso a través de la
API de PressReader. A diferencia de otros scrapers (Reforma, Jornada),
trabaja con ediciones mensuales y requiere autenticación con Bearer
token.

La gestión del token (login, logout, liveness, persistencia) vive en
`source.scraper.pressreader_auth`. Este módulo solo consume tokens.

Flujo de la API de PressReader (una vez autenticado):
1. GET /IssueInfo/GetIssueInfoByCid?cid=24em&issueDate=YYYYMMDD -> Issue ID
2. GET /pagesMetadata/?issue={issue_id} -> páginas y lista de artículos
3. GET /Articles/GetItems?articles[]={id} -> contenido completo
"""

from datetime import date
from typing import List

from source.models import ScrapedRecord, Source
from profile_auth.models import User
from source.scraper.articles import ArticleScraper, MainScraper, ManagerScraper
from source.scraper.scraper_base import get_json_content
from source.scraper.pressreader_auth import (
    PRESSREADER_API_BASE,
    get_pressreader_headers,
    get_pressreader_token,
)


# CID de Proceso en PressReader
PROCESO_CID = "24em"

class ProcesoManagerScraper(ManagerScraper):
    """
    Manager del scraper de Proceso.

    La sesión contra PressReader es gestionada por
    `source.scraper.pressreader_auth` y persistida en el modelo
    `PressReaderSession`. Para liberar el slot manualmente, correr
    `python manage.py close_pressreader_session`.
    """

    date_format = "%Y%m%d"

    def __init__(
        self,
        from_date: str | date | None,
        to_date: str | date | None,
        recover_record: ScrapedRecord | None = None,
        user: User | None = None,
    ) -> None:
        super().__init__(
            from_date,
            to_date,
            main_scraper_class=ProcesoMainScraper,
            article_scraper_class=ProcesoArticleScraper,
            recover_record=recover_record,
            user=user,
        )

    def get_source(self) -> Source:
        if not hasattr(self, "source") or not self.source:
            self.source, _ = Source.objects.get_or_create(
                main_url="https://www.proceso.com.mx",
                defaults={"name": "Proceso", "is_news": True},
            )
        return self.source

    def scrape_sections(self):
        """
        Override para consultar el calendario y obtener solo las fechas con issues disponibles.
        """
        from source.scraper.articles import date_in_date

        from_date = date_in_date(self.scraped_record.from_date)
        to_date = date_in_date(self.scraped_record.to_date)

        # Obtener token para consultar el calendario
        bearer_token = get_pressreader_token()

        # Consultar calendario para obtener fechas reales con issues
        str_dates = self._get_available_issues(
            from_date, to_date, bearer_token)

        if not str_dates:
            print(f"No se encontraron issues disponibles entre {from_date} y {to_date}")
            self.scraped_record.data = {}
            self.scraped_record.save()
            return

        print(f"Encontrados {len(str_dates)} issues: {str_dates}")

        articles_by_date = {}

        for date_ in str_dates:
            try:
                sections_dict = self.main_scraper_class(date_).sections_dict
                print(f"✓ Secciones obtenidas para fecha {date_}: {list(sections_dict.keys())}")
            except Exception as e:
                self.add_error(
                    f"Error getting sections for date {date_}",
                    exception=e,
                )
                continue
            articles_by_date[date_] = sections_dict

        self.scraped_record.data = articles_by_date
        self.scraped_record.save()

    # Si recibimos más de un día, necesitamos revisar si hay issues disponibles para cada día
    def _get_available_issues(
        self, from_date: date, to_date: date, bearer_token: str
    ) -> List[str]:
        """
        Consulta el calendario de PressReader para obtener las fechas que realmente tienen issues.

        Args:
            from_date: Fecha inicial del rango
            to_date: Fecha final del rango
            bearer_token: Token de autenticación de PressReader

        Returns:
            Lista de fechas en formato YYYYMMDD que tienen issues disponibles
        """
        headers = get_pressreader_headers(bearer_token)

        # El endpoint del calendario no usa /se2skyservices
        calendar_url = (
            f"{PRESSREADER_API_BASE}/calendar/get?cid={PROCESO_CID}"
        )

        try:
            calendar_response = get_json_content(calendar_url, custom_headers=headers)
        except Exception as e:
            print(f"Error al obtener calendario: {e}")
            return []

        available_dates = []

        # El calendario tiene formato: {"Years": {"2025": {"12": {"1": {...}}}}}
        years = calendar_response.get("Years", {})

        for year_str, months in years.items():
            year = int(year_str)

            # Filtrar por rango de fechas
            if year < from_date.year or year > to_date.year:
                continue

            for month_str, days in months.items():
                month = int(month_str)

                for day_str in days.keys():
                    day = int(day_str)

                    # Crear fecha y verificar que esté en el rango
                    issue_date = date(year, month, day)

                    # Convertir from_date y to_date a date si son datetime
                    from_date_cmp = (
                        from_date.date() if hasattr(from_date, "date") else from_date
                    )
                    to_date_cmp = (
                        to_date.date() if hasattr(to_date, "date") else to_date
                    )

                    if from_date_cmp <= issue_date <= to_date_cmp:
                        # Formato YYYYMMDD
                        available_dates.append(issue_date.strftime("%Y%m%d"))

        return sorted(available_dates)


class ProcesoMainScraper(MainScraper):
    parser = "json"  # We don't use Beautiful Soup
    need_proxy = False

    # Atributos específicos de PressReader
    bearer_token: str
    issue_id: str | None
    cid: str = PROCESO_CID

    def __init__(self, scraper_date: date | str):
        """
        Inicializa el scraper para una fecha específica.
        Args:
            scraper_date: Fecha en formato YYYYMMDD o date object
        """
        self.bearer_token = get_pressreader_token()
        self.issue_id = None
        self.sections_dict = {}
        self.date_format = "%Y%m%d"
        super().__init__(scraper_date)

    def main_url(self) -> str:
        """URL para obtener información del issue."""
        return (
            f"{PRESSREADER_API_BASE}/IssueInfo/GetIssueInfoByCid"
            f"?cid={self.cid}&issueDate={self.scraper_date}"
        )

    def get_headers(self) -> dict:
        """Headers con autenticación para la API."""
        return get_pressreader_headers(self.bearer_token)

    def set_issue_info(self):
        """
        Obtiene y almacena la información del issue para la fecha dada,
        incluyendo el issue_id necesario para consultas posteriores.
        """
        headers = self.get_headers()

        try:
            issue_response = get_json_content(
                self.main_url(), custom_headers=headers)
            if not issue_response or "Issue" not in issue_response:
                print(f"No se encontró issue para la fecha {self.scraper_date}")
                return None
            self.issue_id = issue_response["Issue"].get("Issue")
            if not self.issue_id:
                print(f"No se pudo obtener el ID del issue para la fecha {self.scraper_date}")
                return None
        except Exception as e:
            print(f"Error al obtener información del issue: {e}")
            return None
        return self.issue_id

    def get_sections(self):
        """
        Obtiene la estructura del issue desde PressReader.
        Las "secciones" en Proceso son las páginas de la revista.
        """
        issue_id = self.set_issue_info()
        if not issue_id:
            return

        # Paso 2: Obtener los títulos por RootArticleId
        pages_url = f"{PRESSREADER_API_BASE}/pagesMetadata/?issue={self.issue_id}"
        headers = self.get_headers()
        titles_dict = {}
        try:
            pages_response = get_json_content(pages_url, custom_headers=headers)
        except Exception as e:
            print(f"Error 1 al obtener páginas: {e}")
            return
        for page in pages_response:
            for article in page.get("Articles", []):
                root_article_id = article.get("RootArticleId")
                str_article_id = str(root_article_id)
                titles_dict[str_article_id] = {
                    "title":  article.get("Title", ""),
                    "subtitle": article.get("Subtitle", ""),
                }

        # Paso 2: Obtener metadata de páginas
        section_pages_url = (f"https://s.prcdn.co/services/layout/"
                     f"?issue={self.issue_id}&version=3")

        try:
            section_pages_response = get_json_content(section_pages_url)
        except Exception as e:
            print(f"Error 2 al obtener páginas: {e}")
            return

        # Paso 3: Organizar por páginas (secciones)
        self.sections_dict = {}

        # La API retorna una lista directamente, no un dict con "Pages"
        pages_list = section_pages_response.get("Pages", [])
        exclude_sections = ["PORTADA", "CONTENTS", "ÍNDICE"]
        # article_home: uid -> sección donde quedó registrado el artículo.
        # Un artículo puede aparecer listado en páginas de varias secciones
        # (reportajes largos cruzando fronteras de sección); lo guardamos
        # una sola vez en su primera sección y acumulamos páginas ahí.
        article_home: dict[str, str] = {}
        base_url = (f"https://proceso.pressreader.com/proceso"
                    f"/{self.scraper_date}/page")

        for page in pages_list:
            section_name = page.get("SectionName", "").upper()
            if section_name in exclude_sections:
                continue
            page_number = page.get("PageNumber", 0)
            self.sections_dict.setdefault(section_name, {"articles": {}})

            for article_data in page.get("Articles", []):
                root_article_id = article_data.get("RootArticleId")
                if not root_article_id:
                    continue
                str_uid = str(root_article_id)

                if str_uid in article_home:
                    home = article_home[str_uid]
                    self.sections_dict[home]["articles"][str_uid]\
                        ["metadata"]["pages"].append(page_number)
                    continue

                article_home[str_uid] = section_name
                title_data = titles_dict.get(str_uid, {})
                self.sections_dict[section_name]["articles"][str_uid] = {
                    "uid": str_uid,
                    "url": f"{base_url}/{page_number}/textview",
                    "title": title_data.get("title", ""),
                    "subtitle": title_data.get("subtitle", ""),
                    "metadata": {
                        "article_id": str_uid,
                        "issue_id": self.issue_id,
                        "pages": [page_number],
                    }
                }

    def get_articles(self):
        """
        Obtiene el contenido completo de los artículos desde la API.
        """

        for section_name, section_data in self.sections_dict.items():
            articles = section_data.get("articles", {})
            self.sections_dict[section_name]["articles"] = list(articles.values())


class ProcesoArticleScraper(ArticleScraper):
    """
    Scraper de artículos individuales de Proceso.
    Como los datos ya vienen de la API, principalmente formatea el contenido.
    """

    need_proxy = False
    parser = "json"  # We don't use Beautiful Soup

    def get_article_data(self):

        """
        Extrae datos del artículo.
        La mayoría ya viene en metadata.api_data de la API de PressReader.
        """
        import json
        articles_url = (f"{PRESSREADER_API_BASE}/articles/"
                        f"GetItems?comment=LatestByAll"
                        f"&viewType=text&articles={self.article.uid}"
                        f"&IsHyphenated=true&options=1")
        bearer_token = get_pressreader_token()
        headers = get_pressreader_headers(bearer_token)
        articles_response = get_json_content(
            articles_url, custom_headers=headers
        )
        articles_data = articles_response.get("Articles", [])
        if len(articles_data) > 1:
            print(
                f"      ⚠ Más de un artículo retornado para {self.article.uid}"
            )
        api_article = articles_data[0] if articles_data else {}
        metadata = self.article.metadata or {}
        self.title = api_article.get("Title") or self.article.title or ""
        self.subtitle = api_article.get("Subhead") or self.article.subtitle
        self.author = api_article.get("Byline")
        pages = metadata.get("pages", [])
        self.pages = ", ".join(str(p) for p in pages)
        self.images = []
        photos = api_article.get("Images", []) or []
        for photo in photos:
            self.images.append(
                {
                    "src": photo.get("Url"),
                    "caption": photo.get("Title", ""),
                }
            )
        blocks = api_article.get("Blocks", [])
        if blocks:
            self.article.html_content = json.dumps(blocks)
        text_content = ""
        self.paragraphs = []
        if blocks:
            for block in blocks:
                block_text = block.get("Text", "")
                if block_text:
                    text_content += block_text + "\n\n"
                    self.paragraphs.append(block_text.strip())
        self.content = text_content.strip()

    def get_paragraphs(self, content: str | None = None) -> List[str]:
        return self.paragraphs

    def get_main_body(self):
        """
        No usamos HTML para Proceso, retornamos None.
        El contenido de texto plano ya está en self.content.
        """
        return None

    def get_reduced_content_text(self):
        self.article.save()

    def special_cleanup(self, body):
        """
        No necesitamos limpieza HTML para Proceso.
        """
        return body


# URLs de referencia de la API de PressReader (documentación)
# Estas constantes documentan el flujo de la API
_API_DOCS = {
    "get_cid": f"{PRESSREADER_API_BASE}/catalog/v1/routes/publication?publication=proceso",
    "get_issue": f"{PRESSREADER_API_BASE}/IssueInfo/GetIssueInfoByCid?cid=24em&issueDate=YYYYMMDD",
    "get_pages": f"{PRESSREADER_API_BASE}/pagesMetadata/?issue={{issue_id}}",
    "get_articles": f"{PRESSREADER_API_BASE}/Articles/GetItems?articles[]={{article_id}}",
    "get_page_keys": f"{PRESSREADER_API_BASE}/IssueInfo/GetPageKeys?issue={{issue_id}}&pageNumber=0&preview=true",
    "get_image": "https://i.prcdn.co/img?file={{issue_id}}&page={{page}}&scale=300&ticket={{ticket}}",
}
