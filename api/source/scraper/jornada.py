from datetime import date

from bs4 import BeautifulSoup
from bs4.element import Tag

from source.models import ScrapedRecord, Source
from profile_auth.models import User
from source.scraper.articles import (
    ArticleScraper, MainScraper, ManagerScraper)
from source.scraper.scraper_base import (
    get_content, get_clean_text, ScraperSession)


# Secciones cuya URL no sirve un listado sino el artículo mismo: el
# editorial del día y la recopilación de cartas de lectores.
SINGLE_ARTICLE_SECTIONS = {"Editorial", "El Correo Ilustrado"}

JORNADA_MAIN_URL = "https://www.jornada.com.mx/"


def single_article_payload(section_name: str, section_url: str) -> dict:
    """Artículo único para una sección que no lista nada.

    Devuelve `uid` y `url` relativos al día; `absolutize_article` los
    completa igual que a los del listado.
    """
    slug = section_url.rstrip("/").split("/")[-1]
    return {
        "uid": slug,
        "title": section_name,
        "url": slug,
        "images": [],
        "content": "",
    }


def absolutize_article(
        article: dict, scraper_date: str, main_url: str) -> dict:
    """Antepone fecha y dominio al `uid` y la `url` relativos.

    Vive aquí y no dentro del scraper porque la recuperación histórica
    arma sus artículos sin pedir el índice del día: si duplicara la
    fórmula del `uid`, un cambio de formato produciría artículos nuevos
    en vez de reusar los existentes por `unique_together`.
    """
    article["url"] = f"{main_url}{article.get('url')}"
    article["uid"] = f"{scraper_date}/{article.get('uid')}"
    return article


class JornadaManagerScraper(ManagerScraper):
    warmup_url = "https://www.jornada.com.mx/"

    def __init__(
            self, from_date: str | date | None, to_date: str | date | None,
            recover_record: ScrapedRecord | None = None,
            user:User | None = None,
            session: ScraperSession | None = None
    ) -> None:
        super().__init__(
            from_date, to_date, JornadaMainScraper, JornadaArticleScraper,
            recover_record=recover_record, user=user, session=session
        )

    def get_source(self) -> Source:
        if not hasattr(self, "source"):
            self.source, _ = Source.objects.get_or_create(
                main_url="https://www.jornada.com.mx/", defaults={
                    "name": "La Jornada",
                    "is_news": True
                })
        return self.source


class JornadaMainScraper(MainScraper):
    need_proxy = True

    def __init__(
            self, scraper_date: date | str,
            session: ScraperSession | None = None):
        self.scraper_date = self.date_in_str(scraper_date)
        self.soup_content = get_content(
            self.main_url(), self.parser, self.need_proxy, session=session)

        super().__init__(scraper_date, session=session)

        for _, section_data in self.sections_dict.items():
            if "articles" not in section_data:
                continue
            for article in section_data["articles"]:
                absolutize_article(
                    article, str(scraper_date), self.main_url())

    def main_url(self):
        return f"https://www.jornada.com.mx/{self.scraper_date}/"

    def get_sections(self):
        self.sections_dict = {}
        excluded_sections = [
            "Mundo", "Espectáculos", "Deportes", "Cartones", "Ciencias"]
        main_sections = self.soup_content.find(
            "div", class_="main-sections gui menu")
        if main_sections:
            for td in main_sections.find_all("td"):  # type: ignore
                if "SECTIONS MENU" in td.decode_contents():  # type: ignore
                    a_tag = td.find("a")  # type: ignore
                    div_tag = a_tag.find(  # type: ignore
                        "div") if a_tag else None
                    if a_tag and div_tag and "href" in a_tag.attrs:  # type: ignore
                        section_name = div_tag.text.strip()  # type: ignore
                        if section_name in excluded_sections:
                            continue
                        section_url = a_tag["href"]  # type: ignore
                        if section_name:
                            self.sections_dict[section_name] = {
                                "url": section_url}

    def get_articles(self):
        for section_name, section_data in self.sections_dict.items():
            section_url = section_data["url"]
            if section_name in SINGLE_ARTICLE_SECTIONS:
                section_data["articles"] = [
                    self.single_article(section_name, section_url)]
                continue
            try:
                section_data["articles"] = JornadaSectionScraper(
                    section_url, session=self.session,
                    referer=self.main_url()).articles
            except Exception as e:
                section_data["error"] = str(e)
                continue
            if not section_data["articles"]:
                # Sin error pero sin artículos: casi siempre es el selector
                # que dejó de coincidir, no una sección vacía de verdad.
                section_data["empty"] = True

    def single_article(self, section_name: str, section_url: str) -> dict:
        return single_article_payload(section_name, section_url)


class JornadaSectionScraper:
    need_proxy = True
    soup_content: BeautifulSoup
    articles: list[dict]

    def __init__(
            self, url: str, session: ScraperSession | None = None,
            referer: str | None = None):
        self.soup_content = get_content(
            f"https://www.jornada.com.mx{url}", with_proxy=self.need_proxy,
            session=session, referer=referer)
        self.get_articles()

    def get_articles(self):

        article_containers = self.soup_content.find_all(
            "div", class_=["itemfirst", "item start", "item"])

        self.articles = []

        for container in article_containers:

            link = container.find(  # type: ignore
                "a", class_="cabeza", href=True)   # type: ignore
            if link:
                title = link.get_text()
                url = link["href"]  # type: ignore
            else:
                continue

            images = [img["src"] for img in container.find_all(  # type: ignore
                "img", src=True)]

            content_texts = [p.get_text() for p in container.find_all(  # type: ignore
                "p", class_=lambda x: x != "more")]

            footer = container.find("div", class_="pie-foto")  # type: ignore
            footer_text = footer.get_text() if footer else ""

            article_content = " ".join(content_texts) + " " + footer_text
            url = str(url)
            article = {
                "uid": url.split("/")[-1] if url else None,
                "title": title,
                "url": url,
                # "imgs": images,
                "images": images,
                "content": article_content
            }

            self.articles.append(article)


class JornadaArticleScraper(ArticleScraper):
    need_proxy = True

    def get_article_data(self):

        article = self.soup_content.find('article')
        title_div = article.find('div', class_='cabeza')

        if title_div:
            self.title = get_clean_text(title_div)
        else:
            self.title = ""

        subtitles = []
        if sumarios := article.find_all('div', class_='sumarios'):
            for sumario in sumarios:
                sumario_text = get_clean_text(sumario)
                if sumario_text:
                    subtitles.append(sumario_text)
        self.subtitle = "\n ".join(subtitles).strip()
        # contents = [p.get_text() for p in article.find_all('p')]
        contents = []
        for p in article.find_all('p'):
            text = get_clean_text(p)
            # if text and text not in titles:
            contents.append(text)
        if initial := article.find('div', class_='inicial'):
            char = get_clean_text(initial)
            if char:
                contents[0] = f"{char}{contents[0]}"
        self.content = "\n\n".join(contents).strip()
        self.images = []
        for photo in article.find_all('div', class_='foto'):
            img = photo.find('img', src=True)
            if img:
                self.images.append({
                    "src": img['src'],
                    "caption": photo.get_text(strip=True)
                })
        author_classes = ['credito-autor', 'credito-articulo']
        try:
            self.author = get_clean_text(
                article.find('div', class_=author_classes).find('span'))
        except AttributeError:
            self.author = None
        if not self.author:
            span_author = article.find('span', itemprop='name')
            # get_clean_text normaliza: los spans vacíos traen "\n", que es
            # truthy y se guardaba tal cual como autor.
            self.author = get_clean_text(span_author) if span_author else None
        self.author = self.author or None

    def get_main_body(self) -> Tag:
        return self.soup_content.find('article')

    def special_cleanup(self, body):
        # Decompose <a> with id = "page_link_prev" and "page_link_next"
        classes_to_remove = [
            'go gui', 'go gui top',
            'credito-autor', 'hemero', 'email', 'credito-titulo',
            'cabeza', 'credito-articulo', 'credito-autor',
            'sumarios']
        for a in body.find_all('div', class_=classes_to_remove):
            a.decompose()

        return body


sections_names_dict = {
    "Nacional": "national",
    "Política": "politica",
    "Economía": "economia",
    "Sociedad": "sociedad",
    "Sociedad y Justicia": "sociedad",
    "Cultura": "cultura",
    "Opinión": "opinion",
    "Estados": "estados",
    "El Correo Ilustrado": "correo",
    "Capital": "capital",
}


