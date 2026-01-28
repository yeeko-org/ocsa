import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Type

import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag
from django.conf import settings

from source.models import Article, ArticleQualify, QualifySchema, ScrapedRecord, Source

REQUESTS_DEFAULT_HEADERS = {"User-Agent": "Mozilla/4.0"}


def get_json_content(
    url: str,
    with_proxy: bool = False,
    attempts: int = 1,
    custom_headers: dict | None = None,
) -> dict:
    """
    Hace requests a APIs JSON con headers personalizados.

    Args:
        url: URL de la API
        with_proxy: Si usar proxy
        attempts: Número de intento actual (para reintentos)
        custom_headers: Headers personalizados (ej: Bearer token)

    Returns:
        dict: Respuesta JSON parseada
    """
    import time

    headers = custom_headers or REQUESTS_DEFAULT_HEADERS
    proxy_key = settings.PROXY_KEY

    if with_proxy and proxy_key:
        proxies = {
            "http": f"http://{proxy_key}",
            "https": f"https://{proxy_key}",
        }
        response = requests.get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        if attempts <= 3:
            print(
                f"Intento {attempts} fallido para {url}. Status: {response.status_code}"
            )
            time.sleep(2**attempts)
            return get_json_content(url, with_proxy, attempts + 1, custom_headers)
        else:
            raise Exception(
                f"Error al acceder a la API: {response.status_code} - {response.text[:200]}"
            )


def get_content(
    url, parser="html.parser", with_proxy: bool = False, attempts: int = 1
) -> BeautifulSoup:
    import time

    proxy_key = settings.PROXY_KEY
    if with_proxy and proxy_key:
        proxies = {
            "http": f"http://{proxy_key}",
            "https": f"https://{proxy_key}",
        }
        response = requests.get(url, headers=REQUESTS_DEFAULT_HEADERS, proxies=proxies)
    else:
        response = requests.get(url, headers=REQUESTS_DEFAULT_HEADERS)
    if response.status_code == 200:
        return BeautifulSoup(response.text, parser)
    else:
        if attempts <= 3 and with_proxy:
            print(f"Intento {attempts} fallido para {url}.")
            time.sleep(2**attempts)
            return get_content(url, parser, with_proxy, attempts + 1)
        else:
            raise Exception(f"Error al acceder a la página: {response.status_code}")


def get_clean_text(elem: PageElement) -> str:
    """
    Obtiene el texto limpio de un Tag de BeautifulSoup, eliminando espacios
    adicionales y saltos de línea.
    """
    text = elem.get_text(separator=" ")
    text = re.sub(r"\n+", " ", text)  # Reemplaza saltos de línea por espacio
    return re.sub(r"\s+", " ", text).strip()


class MainScraper(ABC):
    """
    diccionario esperado:
    {
        "section_name": {
            "url": "url_section",
            "articles": [
                {
                    "uid": "uid",
                    "title": "title",
                    "url": "url",
                    "imgs": "imgs",
                    "content": "content",
                    "metadata": {}
                }
            ]
        }
    }
    """

    soup_content: BeautifulSoup
    sections_dict: Dict[str, dict]
    scraper_date: str
    parser = "html.parser"
    need_proxy = False

    def __init__(self, scraper_date: date | str):
        self.scraper_date = date_in_str(scraper_date)
        self.soup_content = get_content(self.main_url(), self.parser, self.need_proxy)

        self.get_sections()
        self.get_articles()

    @abstractmethod
    def main_url(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_sections(self):
        raise NotImplementedError

    @abstractmethod
    def get_articles(self):
        raise NotImplementedError


class ArticleScraper(ABC):
    article: Article
    soup_content: BeautifulSoup

    title: str
    subtitle: str | None
    author: str | None
    content: str
    images: List[dict[str, Any]] | None
    ai_engine: str | None
    parser = "html.parser"
    need_proxy: bool = False

    def __init__(self, article: Article, update: bool = False):
        self.article = article
        if article.html_content and not update:
            self.soup_content = BeautifulSoup(article.html_content, self.parser)
            self.get_article_data()
            return
        self.soup_content = get_content(self.article.url, self.parser, self.need_proxy)
        try:
            self.get_article_data()
        except Exception as e:
            print(f"Error getting article data: {e}")
            return

        article.title = self.title or article.title
        article.subtitle = self.subtitle or article.subtitle
        article.author = self.author or article.author
        article.content = self.content or article.content
        article.paragraphs = self.get_paragraphs(article.content)
        # article.paragraps = self.content.split("\n") if self.content else []
        article.html_content = str(self.get_main_body()) or article.html_content
        article.images = self.images or article.images  # type: ignore

    @abstractmethod
    def get_article_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_main_body(self) -> Tag:
        raise NotImplementedError

    @abstractmethod
    def special_cleanup(self, body: Tag) -> Tag:
        raise NotImplementedError

    def get_paragraphs(self, content: str | None = None) -> List[str]:
        if not content:
            return []

        paragraphs = re.split(r"\n{2,}", content)
        final_paragraphs = []
        for paragraph in paragraphs:
            single_line = paragraph.replace("\n", " ").strip()
            if paragraph:
                final_paragraphs.append(single_line)
        return final_paragraphs

    def get_reduced_content_text(self):
        body = self.get_main_body()
        if not body:
            return
        title = self.title
        # print("Body1:", body)
        # if title not in body.get_text():
        #     title = None

        excluded_tags = [
            "script",
            "style",
            "noscript",
            "svg",
            "button",
            "input",
            "textarea",
            "select",
            "option",
            "form",
            "fieldset",
            "canvas",
            "nav",
            "aside",
            "address",
            "map",
            "area",
            "legend",
            "iframe",
            "embed",
            "object",
            "param",
            "video",
            "audio",
        ]
        for excluded_tag in excluded_tags:
            for tag in body.find_all(excluded_tag):
                tag.decompose()
        main_tags = [
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "ul",
            "div",
            "span",
            "article",
            "section",
            "header",
            "footer",
            "img",
            "video",
            "figure",
            "figcaption",
            "blockquote",
            "table",
            "tr",
            "td",
            "th",
            "ol",
            "dl",
            "dt",
            "ddem",
            "strong",
            "b",
            "i",
            "a",
            "br",
        ]
        begin_title = not bool(title)
        for tag in body.find_all():
            tag_text = tag.get_text(strip=True)
            # print(f"Tag: {tag.name}, Text: {tag_text}")
            if not tag_text and tag.name not in main_tags:
                tag.decompose()
            if not begin_title:
                direct_text = tag.string
                if direct_text and title in direct_text:
                    begin_title = True
            if not begin_title:
                if title in tag_text:
                    tag.decompose()

        # body = self.special_cleanup(body)

        allowed_attrs = ["class", "id", "href", "src", "alt", "title"]
        # new_body = BeautifulSoup('', 'html.parser')
        for tag in body.find_all():
            relevant_attrs = {
                key: value for key, value in tag.attrs.items() if key in allowed_attrs
            }
            tag.attrs = relevant_attrs
        try:
            # body_encoding = body.encode("utf-8")
            self.article.html_content = (
                body.prettify().encode("utf-8", errors="ignore").decode("utf-8")
            )
            # print("Body4:", self.htmml_content)
        except Exception as e:
            print("Error body.pretty:", e)
            print("-" * 50)
            print("Body5:", body)
            raise e
        # new_html = body.prettify()
        # self.article.content = body.get_text(separator="\n")
        # self.article.paragraphs = self.get_paragraphs(self.article.content)
        self.article.save()


def date_in_str(date_: date | str) -> str:
    if isinstance(date_, date):
        return date_.strftime("%Y/%m/%d")

    pattern = r"^\d{4}/\d{2}/\d{2}$"
    pattern2 = r"^\d{4}\d{2}\d{2}$"
    if not re.match(pattern, date_) and not re.match(pattern2, date_):
        raise ValueError("Invalid date format. Must be YYYY/MM/DD or YYYYMMDD")

    return date_
