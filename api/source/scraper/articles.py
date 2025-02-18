from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import json
import re
from typing import Any, Dict, List, Type

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from source.models import Article, ScrapedRecord, Source
from utils.open_ai import JsonRequestOpenAI
from django.conf import settings

REQUESTS_DEFAULT_HEADERS = {'User-Agent': 'Mozilla/4.0'}
PRECLASSIFY_ARTICLES_BLOCK = getattr(
    settings, "PRECLASSIFY_ARTICLES_BLOCK", 500)


def get_content(url) -> BeautifulSoup:

    response = requests.get(url, headers=REQUESTS_DEFAULT_HEADERS)
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
    scraped_record: ScrapedRecord
    main_scraper_class: Type["MainScraper"]
    article_scraper_class: Type["ArticleScraper"]

    date_format = "%Y/%m/%d"
    source: Source
    articles_by_date: Dict[str, dict]
    articles_for_openAI: list
    articles_by_id: Dict[int, Article]
    overlapping_dates: list
    errors: list
    pre_classify_response: Any
    pre_classify_request: JsonRequestOpenAI

    open_ai_engine: str | None

    def __init__(
            self, from_date: str | date, to_date: str | date,
            main_scraper_class: Type["MainScraper"],
            article_scraper_class: Type["ArticleScraper"],
            recover_record: ScrapedRecord | None = None,
            open_ai_engine: str | None = None

    ) -> None:
        self.main_scraper_class = main_scraper_class
        self.article_scraper_class = article_scraper_class
        self.overlapping_dates = []
        self.articles_by_id = {}
        self.errors = []
        self.open_ai_engine = open_ai_engine
        self.scraped_record = None

        if recover_record:
            self.scraped_record = recover_record
            self.source = recover_record.source or self.get_source()
            return

        if not self.check_overlapping_records(from_date, to_date):
            return

        self.scraped_record = ScrapedRecord.objects.create(
            source=self.get_source(), from_date=date_in_date(from_date),
            to_date=date_in_date(to_date))

    def add_error(self, error: str, exception: Exception | None = None):
        if exception:
            raise exception
        if not self.scraped_record:
            self.errors.append(f"{error}: {exception or ''}")
            return

        if not self.scraped_record.errors:
            self.scraped_record.errors = []

        self.scraped_record.errors.append(f"{error}: {exception or ''}")
        self.scraped_record.save()

    def check_overlapping_records(self, from_date, to_date):
        from_date = date_in_date(from_date)
        to_date = date_in_date(to_date)

        overlapping_records = ScrapedRecord.objects.filter(
            from_date__lte=to_date,
            to_date__gte=from_date,
            source=self.get_source(),
            status__isnull=False
        ).exclude(status="failed")

        self.overlapping_dates = [
            [record.from_date.strftime("%Y/%m/%d"),
             record.to_date.strftime("%Y/%m/%d")]
            for record in overlapping_records
        ]

        if self.overlapping_dates:
            self.add_error("Ya existen registros para las fechas")
            return False
        return True

    def scrape_sections(self):

        str_dates = get_date_range(
            self.scraped_record.from_date, self.scraped_record.to_date,
            date_out_format=self.date_format)

        articles_by_date = {}

        self.scraped_record.status = "get_sections"
        self.scraped_record.save()

        for date_ in str_dates:

            try:
                sections_dict = self.main_scraper_class(date_).sections_dict
            except Exception as e:
                sections_dict = {
                    "error": f"Error getting sections for date {date_}",
                    "exception": str(e)
                }
            articles_by_date[date_] = sections_dict

        self.scraped_record.data = articles_by_date  # type: ignore
        self.scraped_record.save()

    @abstractmethod
    def get_source(self) -> Source:
        raise NotImplementedError

    def record_articles(self, reset: bool = False):
        self.scraped_record.status = "record_articles"
        self.scraped_record.save()

        self.articles_for_openAI = []
        self.articles_by_id = {}
        for date_, sections_dict in self.scraped_record.data.items():  # type: ignore
            for section_name, section_data in sections_dict.items():
                if section_name in ["error", "exception"]:
                    print(f"Error in {date_}/{section_name} : {section_data}")
                    continue
                for article_data in section_data.get("articles", []):
                    try:
                        self.record_article(
                            article_data, section_name, date_, reset=reset)
                    except Exception as e:
                        article_data.setdefault("errors", []).append(str(e))

        self.scraped_record.save()

    def record_article(
            self, article_data: dict, section_name: str, date_: str,
            reset: bool = False
    ):
        uid = article_data.get("uid") or ""
        title = article_data.get("title")
        url = article_data.get("url")
        if not all([uid, title, url]):
            return
        images = article_data.get("images")
        content = article_data.get("content")
        metadata = article_data.get("metadata")

        defaults = {
            "title": title,
            "url": url,
            "images": images,
            "basic_content": content,
            "metadata": metadata,
            "section": section_name,
            "published_date": date_in_date(date_),
            "scraped": self.scraped_record,
        }

        article_obj, _ = Article.objects.get_or_create(
            uid=uid, source=self.get_source(), defaults=defaults)

        if article_obj.preclassification and not reset:
            return
        article_id = article_obj.id
        self.articles_by_id[article_id] = article_obj

        article_for_ai = {
            "id": article_id,
            "title": title,
            "section": section_name,
        }
        if content:
            article_for_ai["content"] = content
        self.articles_for_openAI.append(article_for_ai)

    def make_preclassify_articles(self):
        self.scraped_record.status = "preclassify"
        self.scraped_record.save()
        if not self.articles_for_openAI:
            return

        len_articles = len(self.articles_for_openAI)
        for i in range(0, len_articles, PRECLASSIFY_ARTICLES_BLOCK):
            self.preclassify_articles(
                self.articles_for_openAI[i:i + PRECLASSIFY_ARTICLES_BLOCK])

        self.scraped_record.save()

    def preclassify_articles(self, articles: List[dict]):
        try:
            # full_prompt = json.dumps(articles)
            simple_articles = {}
            for article in articles:
                title = article.get("title")
                if section := article.get("section"):
                    title = f"{title} ({section})"
                simple_articles[article["id"]] = title
            full_prompt = json.dumps(simple_articles, ensure_ascii=False)
        except TypeError as e:
            print(f"Error converting to json: {e}")
            return

        prompt_path = "source/scraper/prompt_pre_classify.txt"
        # TODO: Lucian, comentemos esto, pero es super difícil de encontrar
        # algunas cosas como el engine, está en muchos lados y no sé si
        # está declarado acá o allá o en dónde y me confundo, pasa mucho en
        # muchos lados y me pierdo entre miles de declaraciones aisladas.
        self.pre_classify_request = JsonRequestOpenAI(
            prompt_path, engine=self.open_ai_engine)

        self.pre_classify_response, request_id = self.pre_classify_request\
            .send_prompt(full_prompt)
        if not self.pre_classify_response:
            print("No response from OpenAI")
            return

        try:
            pre_classify_response_items = self.pre_classify_response.items()  # type: ignore
        except Exception as e:
            self.add_error("Error getting items from response", e)
            return
        if not self.scraped_record.preclassification:
            self.scraped_record.preclassification = []  # type: ignore
        self.scraped_record.preclassification += pre_classify_response_items
        counter = {"maybe": 0, "valid": 0, "invalid": 0, "indirect": 0}
        for article_id, preclassification in pre_classify_response_items:
            # print(f"Preclassification for {uid}: {preclasification}")
            # print(f"objeto: {self.articles_by_uid.get(uid)}")
            if preclassification not in ["valid", "invalid", "maybe", "indirect"]:
                print(f"Invalid preclassification: {preclassification}")
                continue
            # article_obj = self.articles_by_uid.get(uid)
            counter[preclassification] += 1
            article_id = int(article_id)
            article_obj = self.articles_by_id.get(article_id)
            if not article_obj:
                continue

            article_obj.preclassification = preclassification
            article_obj.request_pre_openai = request_id
            article_obj.save()
        print(f"counters: {counter.items()}")

    def full_scrape_articles(self, update: bool = False, check_criteria: bool = True):

        self.scraped_record.status = "criteria"
        self.scraped_record.save()
        # if self.articles_by_uid:
        if self.articles_by_id:
            articles_objects = self.articles_by_id.values()
        else:
            articles_objects = list(Article.objects.filter(
                scraped=self.scraped_record))
        print(f"Full scrape articles for {len(articles_objects)} articles")
        x = 0
        for article_obj in articles_objects:
            x += 1
            if article_obj.preclassification not in ["valid", "maybe", "indirect"]:
                continue

            print(f"Article {x} {article_obj.uid}")
            try:
                article_scraper = self.article_scraper_class(
                    article_obj, update=update,
                    open_ai_engine=self.open_ai_engine)
            except Exception as e:
                self.add_error(
                    f"Error scraping article {article_obj.uid}", e)
            if check_criteria:
                try:
                    article_scraper.get_reduced_content_text()
                    article_scraper.get_criteria()
                except Exception as e:
                    self.add_error(
                        f"Error getting criteria for article {article_obj.uid}", e)


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
    open_ai_engine: str | None

    def __init__(
            self, article: Article, update: bool = False,
            open_ai_engine: str | None = None
    ):
        self.open_ai_engine = open_ai_engine
        self.article = article
        if article.html_content and not update:
            self.soup_content = BeautifulSoup(
                article.html_content, "html.parser")
            self.get_article_data()
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
        article.html_content = str(
            self.get_main_body()) or article.html_content
        article.images = self.images or article.images  # type: ignore
        article.save()

    @abstractmethod
    def get_article_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_main_body(self) -> Tag:
        raise NotImplementedError

    def get_criteria(self):
        article_criteria_request = JsonRequestOpenAI(
            "source/scraper/prompt_article_criteria.txt",
            engine=self.open_ai_engine)

        pre_classify_response, req_id = article_criteria_request\
            .send_prompt(self.article.content)

        if not pre_classify_response:
            print("No response from OpenAI")
            return

        if not isinstance(pre_classify_response, dict):
            print("Invalid response")
            return
        self.article.criteria = pre_classify_response
        self.article.request_criteria_openai = req_id
        self.article.save()

    def get_reduced_content_text(self):
        body = self.get_main_body()
        if not body:
            return
        body = body
        title = self.title
        if title not in body.get_text():
            title = None

        excluded_tags = [
            'script', 'style', 'noscript', 'svg', 'button', 'input',
            'textarea', 'select', 'option', 'form', 'fieldset', 'canvas',
            'nav', 'aside', 'address', 'map', 'area',
            'legend', 'iframe', 'embed', 'object', 'param', 'video', 'audio']
        for excluded_tag in excluded_tags:
            for tag in body.find_all(excluded_tag):
                tag.decompose()
        main_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul']
        begin_title = not bool(title)
        for tag in body.find_all():
            tag_text = tag.get_text(strip=True)
            if not tag_text and tag.name not in main_tags:
                tag.decompose()
            if not begin_title:
                direct_text = tag.string
                if direct_text and title in direct_text:
                    begin_title = True
            if not begin_title:
                if title not in tag_text:
                    tag.decompose()

        allowed_attrs = ['class', 'id', 'href', 'src', 'alt', 'title']
        # new_body = BeautifulSoup('', 'html.parser')
        for tag in body.find_all():
            relevant_attrs = {
                key: value for key, value in tag.attrs.items()
                if key in allowed_attrs
            }
            tag.attrs = relevant_attrs
        try:
            # body_encoding = body.encode("utf-8")
            self.article.html_content = body.prettify()\
                .encode("utf-8", errors="ignore").decode("utf-8")
            # print("Body4:", self.htmml_content)
        except Exception as e:
            print("Error body.pretty:", e)
            print("-" * 50)
            print("Body5:", body)
            raise e
        # new_html = body.prettify()
        self.article.content = body.get_text(separator="\n")
        self.article.save()
