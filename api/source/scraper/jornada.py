from datetime import date

from bs4 import BeautifulSoup

from source.models import Source
from source.scraper.articles import (
    ArticleScraper, MainScraper, ManagerScraper, get_content)


class JornadaManagerScraper(ManagerScraper):
    def set_source(self):
        self.source, _ = Source.objects.get_or_create(
            main_url="https://www.jornada.com.mx/", defaults={
                "name": "La Jornada",
                "is_news": True
            })


class JornadaMainScraper(MainScraper):

    def __init__(self, scraper_date: date | str):
        super().__init__(scraper_date)

        for _, section_data in self.sections_dict.items():
            if "articles" not in section_data:
                continue
            for article in section_data["articles"]:
                article["url"] = f"{self.main_url()}{article.get('url')}"

    def main_url(self):
        return f"https://www.jornada.com.mx/{self.scraper_date}/"

    def get_sections(self):
        self.sections_dict = {}
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
                        section_url = a_tag["href"]  # type: ignore
                        if section_name:
                            self.sections_dict[section_name] = {
                                "url": section_url}

    def get_articles(self):
        for _, section_data in self.sections_dict.items():
            section_url = section_data["url"]
            section_data["articles"] = JornadaSectionScraper(
                section_url).articles


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
                title = link.get_text(strip=True)
                url = link["href"]  # type: ignore
            else:
                continue

            imgs = [img["src"] for img in container.find_all(  # type: ignore
                "img", src=True)]

            content_texts = [p.get_text(strip=True) for p in container.find_all(  # type: ignore
                "p", class_=lambda x: x != "more")]

            footer = container.find("div", class_="pie-foto")  # type: ignore
            footer_text = footer.get_text(strip=True) if footer else ""

            article_content = " ".join(content_texts) + " " + footer_text

            article = {
                "title": title,
                "url": url,
                "imgs": imgs,
                "content": article_content
            }

            self.articles.append(article)


class JornadaArticleScraper(ArticleScraper):

    def get_article_data(self):

        article = self.soup_content.find('article')
        self.title = article.find('div', class_='cabeza')\
            .get_text(strip=True)
        self.author = article.find('div', class_='credito-autor')\
            .find('span').get_text(strip=True)
        self.content = "\n".join(
            [p.get_text(strip=True) for p in article.find_all('p')])
        self.images = [img['src'] for img in article.find_all('img', src=True)]
