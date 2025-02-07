from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import json
import re
from typing import Dict, List, Type

import requests
from bs4 import BeautifulSoup

from source.models import Article, ScrapedRecord, Source
from utils.open_ai import JsonRequestOpenAI


def get_content(url) -> BeautifulSoup:
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        raise Exception(
            f"Error al acceder a la página: {response.status_code}")


def date_in_str(date_: date | str) -> str:
    if isinstance(date_, date):
        return date_.strftime("%Y/%m/%d")

    pattern = r"^\d{4}/\d{2}/\d{2}$"
    if not re.match(pattern, date_):
        raise ValueError("Invalid date format. Must be YYYY/MM/DD")

    return date_


def date_in_date(date_: str | date) -> date:
    if isinstance(date_, date):
        return date_
    try:
        return datetime.strptime(date_, "%Y/%m/%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Must be YYYY/MM/DD: {e}")


def get_date_range(
        from_date: str | date, to_date: str | date,
        date_out_format: str = "%Y/%m/%d"
) -> List[str]:

    from_date = date_in_date(from_date)
    to_date = date_in_date(to_date)

    if from_date > to_date:
        raise ValueError(
            "'from_date' debe ser anterior o igual a 'to_date'")

    date_list = []
    current_date = from_date
    while current_date <= to_date:
        date_list.append(current_date.strftime(date_out_format))
        current_date += timedelta(days=1)

    return date_list


class ManagerScraper(ABC):
    date_format = "%Y/%m/%d"
    main_scraper_class: Type["MainScraper"]
    article_scraper_class: Type["ArticleScraper"]
    source: Source
    articles_by_date: Dict[str, dict]
    articles_for_openAI: dict
    articles_by_uid: Dict[str, Article]

    def __init__(
            self, start_date: str | date, end_date: str | date,
            main_scraper_class: Type["MainScraper"]
    ) -> None:
        self.set_source()
        str_dates = get_date_range(
            start_date, end_date, date_out_format=self.date_format)
        main_scraper_class = main_scraper_class
        self.articles_by_date = {}

        ScrapedRecord.objects.create(
            source=self.source, date_from=start_date, date_to=end_date)

        for date_ in str_dates:
            # TODO: Verificar si ya se exploro esta fecha?

            sections_dict = main_scraper_class(date_).sections_dict
            self.articles_by_date[date_] = sections_dict

    @abstractmethod
    def set_source(self):
        raise NotImplementedError

    def record_articles(self):
        self.articles_for_openAI = {}
        self.articles_by_uid = {}
        for date_, sections_dict in self.articles_by_date.items():
            for section_name, section_data in sections_dict.items():
                for article_data in section_data.get("articles", []):
                    # TODO: agregar en los scrapers un uid para identificar el articulo
                    self.check_article(article_data, section_name, date_)

    def check_article(self, article_data: dict, section_name: str, date_: str):
        uid = article_data.get("uid") or ""
        title = article_data.get("title")
        url = article_data.get("url")
        if not all([uid, title, url]):
            return
        imgs = article_data.get("imgs")
        content = article_data.get("content")
        metadata = article_data.get("metadata")

        defaults = {
            "title": title,
            "url": url,
            "imgs": imgs,
            "basic_content": content,
            "metadata": metadata,
            "section": section_name,
            "published_date": date_in_date(date_)
        }

        article_obj, _ = Article.objects.get_or_create(
            uid=uid, source=self.source, defaults=defaults)

        if article_obj.preclasification:
            return

        self.articles_for_openAI[uid] = {
            "title": title,
            "content": content,
            "uid": uid
        }
        self.articles_by_uid[uid] = article_obj

    def get_preclassify_articles_response(self):
        if not self.articles_for_openAI:
            return

        try:
            full_prompt = json.dumps(list(self.articles_for_openAI.values()))
        except TypeError as e:
            print(f"Error converting to json: {e}")

        pre_classify_request = JsonRequestOpenAI(
            "source/scraper/prompt_pre_clasify.txt")

        pre_classify_response = pre_classify_request.send_prompt(full_prompt)
        if not pre_classify_response:
            print("No response from OpenAI")
            return

        """
        {
            "1": "válido",
            "6": "invalido",
            "7": "podría ser"
        }
        """
        try:
            pre_classify_response_items = pre_classify_response.items()  # type: ignore
        except Exception as e:
            print(f"Error getting items from response: {e}")
            return

        for uid, preclasification in pre_classify_response_items:
            if preclasification not in ["válido", "invalido", "podría ser"]:
                continue
            article_obj = self.articles_by_uid.get(uid)
            if not article_obj:
                continue

            article_obj.preclasification = preclasification
            article_obj.save()

    def full_scrape_articles(self, update: bool = False, check_criteria: bool = False):
        for _, article_obj in self.articles_by_uid.items():

            if article_obj.preclasification in ["válido", "podría ser"]:
                article_scraper = self.article_scraper_class(
                    article_obj, update=update)
                if check_criteria:
                    article_scraper.get_criteria()


class MainScraper(ABC):
    """
    diccionario esperado:
    {
        "section_name": {
            "url": "url_section",
            "articles": [
                {
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

    def __init__(self, scraper_date: date | str):
        self.scraper_date = date_in_str(scraper_date)
        self.soup_content = get_content(self.main_url())

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
    author: str | None
    content: str
    images: List[str]

    def __init__(self, article: Article, update: bool = False):
        self.article = article
        if article.content and not update:
            return
        self.soup_content = get_content(article.url)
        try:
            self.get_article_data()
        except Exception as e:
            print(f"Error getting article data: {e}")
            return

        article.title = self.title or article.title
        article.autor = self.author or article.autor
        article.content = self.content or article.content
        article.images = self.images or article.images  # type: ignore
        article.save()

    @abstractmethod
    def get_article_data(self):
        raise NotImplementedError

    def get_criteria(self):
        article_criteria_request = JsonRequestOpenAI(
            "source/scraper/prompt_article_criteria.txt")

        pre_classify_response = article_criteria_request\
            .send_prompt(self.article.content)

        if not pre_classify_response:
            print("No response from OpenAI")
            return
        
        # TODO: Guardar criterios en el modelo
