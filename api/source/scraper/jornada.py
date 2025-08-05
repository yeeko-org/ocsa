from datetime import date

from bs4 import BeautifulSoup
from bs4.element import Tag

from source.models import ScrapedRecord, Source
from source.scraper.articles import (
    ArticleScraper, MainScraper, ManagerScraper)
from source.scraper.scraper_base import get_content, get_clean_text


class JornadaManagerScraper(ManagerScraper):

    def __init__(
            self, from_date: str | date, to_date: str | date,
            recover_record: ScrapedRecord | None = None,
            open_ai_engine: str | None = None,
            is_test: bool = False
    ) -> None:
        super().__init__(
            from_date, to_date, JornadaMainScraper, JornadaArticleScraper,
            recover_record=recover_record, open_ai_engine=open_ai_engine,
            is_test=is_test
        )

    def get_source(self) -> Source:
        if not hasattr(self, "_source"):
            self._source, _ = Source.objects.get_or_create(
                main_url="https://www.jornada.com.mx/", defaults={
                    "name": "La Jornada",
                    "is_news": True
                })
        return self._source


class JornadaMainScraper(MainScraper):

    def __init__(self, scraper_date: date | str):
        super().__init__(scraper_date)

        for _, section_data in self.sections_dict.items():
            if "articles" not in section_data:
                continue
            for article in section_data["articles"]:
                article["url"] = f"{self.main_url()}{article.get('url')}"
                article["uid"] = f"{scraper_date}/{article.get('uid')}"

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
        for _, section_data in self.sections_dict.items():
            section_url = section_data["url"]
            try:
                section_data["articles"] = JornadaSectionScraper(
                    section_url).articles
            except Exception as e:
                section_data["error"] = str(e)


class JornadaSectionScraper:
    soup_content: BeautifulSoup
    articles: list[dict]

    def __init__(self, url: str):
        self.soup_content = get_content(f"https://www.jornada.com.mx{url}")
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

    def get_article_data(self):

        article = self.soup_content.find('article')
        title_div = article.find('div', class_='cabeza')
        self.title = get_clean_text(title_div)

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
            self.author = article.find('div', class_=author_classes)\
                .find('span').get_text()
        except AttributeError:
            self.author = None
        if not self.author:
            span_author = article.find('span', itemprop='name')
            if span_author:
                self.author = span_author.get_text()

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

