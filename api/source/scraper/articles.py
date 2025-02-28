from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import json
import re
from typing import Any, Dict, List, Type

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from django.conf import settings
from source.models import (
    Article, ScrapedRecord, Source, ArticleQualify, QualifySchema)
from utils.open_ai import JsonRequestOpenAI

REQUESTS_DEFAULT_HEADERS = {'User-Agent': 'Mozilla/4.0'}
PRECLASSIFY_ARTICLES_BLOCK = getattr(
    settings, "PRECLASSIFY_ARTICLES_BLOCK", 500)


def get_content(url, parser="html.parser") -> BeautifulSoup:

    response = requests.get(url, headers=REQUESTS_DEFAULT_HEADERS)
    if response.status_code == 200:
        return BeautifulSoup(response.text, parser)
    else:
        raise Exception(
            f"Error al acceder a la página: {response.status_code}")


def date_in_str(date_: date | str) -> str:
    if isinstance(date_, date):
        return date_.strftime("%Y/%m/%d")

    pattern = r"^\d{4}/\d{2}/\d{2}$"
    pattern2 = r"^\d{4}\d{2}\d{2}$"
    if not re.match(pattern, date_) and not re.match(pattern2, date_):
        raise ValueError("Invalid date format. Must be YYYY/MM/DD or YYYYMMDD")

    return date_


def date_in_date(date_: str | date) -> date:
    if isinstance(date_, date):
        return date_
    try:
        return datetime.strptime(date_, "%Y/%m/%d")
    except ValueError as e:

        try:
            return datetime.strptime(date_, "%Y%m%d")
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
    parser = "html.parser"
    source: Source
    articles_by_date: Dict[str, dict]
    articles_for_openAI: list
    articles_by_id: Dict[int, Article]
    overlapping_dates: list
    errors: list
    pre_classify_response: Any
    pre_classify_request: JsonRequestOpenAI

    open_ai_engine: str | None
    use_deepseek: bool
    qualify_schema: QualifySchema | None

    def __init__(
            self, from_date: str | date, to_date: str | date,
            main_scraper_class: Type["MainScraper"],
            article_scraper_class: Type["ArticleScraper"],
            recover_record: ScrapedRecord | None = None,
            open_ai_engine: str | None = None,
            is_test: bool = False, use_deepseek: bool = False

    ) -> None:
        self.block_size = PRECLASSIFY_ARTICLES_BLOCK
        self.block_full_articles = 1
        self.main_scraper_class = main_scraper_class
        self.article_scraper_class = article_scraper_class
        self.overlapping_dates = []
        self.articles_by_id = {}
        self.errors = []
        self.open_ai_engine = open_ai_engine
        self.use_deepseek = use_deepseek
        self.scraped_record = None
        self.is_test = is_test

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
        if not all([uid, url]):
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

        if not title:
            return

        article_for_ai = {
            "id": article_id,
            "title": title,
            "section": section_name,
        }
        if content:
            article_for_ai["content"] = content
        self.articles_for_openAI.append(article_for_ai)

    def make_preclassify_articles(
            self, block_size: int = 0, alt_version: bool = False):
        self.scraped_record.status = "preclassify"
        self.scraped_record.save()
        if block_size:
            self.block_size = block_size

        if not self.articles_for_openAI:
            return
        prompt_path = "source/scraper/prompt_pre_classify.txt"
        prompt_version = "preclassify_v1"
        if alt_version:
            prompt_path = "source/scraper/prompt_pre_classify_v2.txt"
            prompt_version = "preclassify_v2"

        if self.is_test:
            self.qualify_schema, _ = QualifySchema.objects.get_or_create(
                scraped_record=self.scraped_record,
                ia_model=self.open_ai_engine,
                prompt_version=prompt_version,
                batch_size=self.block_size)
        else:
            self.qualify_schema = None

        len_articles = len(self.articles_for_openAI)
        print(f"Preclassify articles for {len_articles} articles")
        for i in range(0, len_articles, self.block_size):
            print(f"Preclassifying articles {i} to {i + self.block_size}")
            self.preclassify_articles(
                self.articles_for_openAI[i:i + self.block_size], prompt_path)

        self.scraped_record.save()

    def preclassify_articles(self, articles: List[dict], prompt_path: str):
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
            print(f"Error converting to json art: {e}")
            print("articles:", articles)
            return

        # TODO: Lucian, comentemos esto, pero es super difícil de encontrar
        # algunas cosas como el engine, está en muchos lados y no sé si
        # está declarado acá o allá o en dónde y me confundo, pasa mucho en
        # muchos lados y me pierdo entre miles de declaraciones aisladas.
        self.pre_classify_request = JsonRequestOpenAI(
            prompt_path, engine=self.open_ai_engine,
            use_deepseek=self.use_deepseek)

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
        counter = {"maybe": 0, "valid": 0, "invalid": 0, "unknown": 0}
        for article_id, preclassification in pre_classify_response_items:
            # print(f"Preclassification for {uid}: {preclasification}")
            # print(f"objeto: {self.articles_by_uid.get(uid)}")
            if preclassification not in ["valid", "invalid", "maybe", "unknown"]:
                print(f"Invalid preclassification: {preclassification}")
                continue
            # article_obj = self.articles_by_uid.get(uid)
            counter[preclassification] += 1
            article_id = int(article_id)
            article_obj = self.articles_by_id.get(article_id)
            if not article_obj:
                continue
            is_selected = preclassification in ["valid", "maybe", "unknown"]
            if self.is_test:
                change_value = self.get_change_value(is_selected, article_obj)
                _ = ArticleQualify.objects.create(
                    article=article_obj,
                    qualify_schema=self.qualify_schema,
                    is_selected=is_selected,
                    change_value=change_value,
                    request_id=request_id)
            else:
                article_obj.preclassification = preclassification
                article_obj.save()
        print(f"counters: {counter.items()}")

    def get_change_value(self, is_selected: bool, article_obj: Article):
        if article_obj.is_selected == is_selected:
            return "selected" if is_selected else "not_selected"
        return "plus" if is_selected else "minus"

    def full_scrape_articles(
            self, update: bool = False, check_criteria: bool = True,
            all_articles: bool = False, block_size: int = 0):

        self.scraped_record.status = "criteria"
        self.scraped_record.save()
        if block_size:
            self.block_full_articles = block_size
        if self.is_test:
            self.qualify_schema, _ = QualifySchema.objects.get_or_create(
                scraped_record=self.scraped_record,
                ia_model=self.open_ai_engine,
                prompt_version="criteria_v1",
                batch_size=self.block_full_articles)
        else:
            self.qualify_schema = None
        # if self.articles_by_uid:
        # print("articles_by_id:", bool(self.articles_by_id))
        if self.articles_by_id:
            articles_objects = list(self.articles_by_id.values())
            print("type of articles_objects:", type(articles_objects))
        else:
            articles_objects = list(Article.objects.filter(
                scraped=self.scraped_record))
        len_articles = len(articles_objects)
        print(f"Full scrape articles for {len_articles} articles")
        if not all_articles:
            articles_objects = [
                article for article in articles_objects
                if article.preclassification in ["valid", "maybe", "unknown"]
            ]
        for i in range(0, len_articles, self.block_full_articles):
            init_msg = "Scraping and classifying article"
            if self.block_full_articles > 1:
                print(f"{init_msg}s {i} to {i + self.block_full_articles}")
            elif i % 10 == 0:
                print(f"{init_msg} {i}")
            self.full_scrape_batch(
                articles_objects[i:i + self.block_full_articles],
                update=update, check_criteria=check_criteria)

    def full_scrape_batch(
            self, articles: List[Article], update: bool = False,
            check_criteria: bool = True):
        many_articles = self.block_full_articles > 1
        full_content = ""

        for article in articles:
            if not self.is_test:
                try:
                    article_scraper = self.article_scraper_class(
                        article, update=update)
                except Exception as e:
                    return self.add_error(
                        f"Error scraping article {article.id}", e)
                try:
                    article_scraper.get_reduced_content_text()
                    content = article_scraper.article.content.strip()
                except Exception as e:
                    return self.add_error(
                        f"Error getting criteria for article {article.id}", e)
            else:
                content = article.basic_content.strip()

            if many_articles:
                full_content += f"-- ARTÍCULO {article.id} --\n{content}\n\n"
            else:
                full_content = content
        if not full_content:
            return

        if not check_criteria:
            return

        prompt_criteria = "prompt_articles_criteria.txt" \
            if many_articles else "prompt_article_criteria.txt"
        articles_criteria_request = JsonRequestOpenAI(
            f"source/scraper/{prompt_criteria}",
            engine=self.open_ai_engine, use_deepseek=self.use_deepseek)

        pre_classify_response, req_id = articles_criteria_request\
            .send_prompt(full_content)

        if not pre_classify_response:
            print("No response from OpenAI")
            return

        if not isinstance(pre_classify_response, dict):
            print("Invalid response")
            return
        if not many_articles:
            pre_classify_response = {articles[0].id: pre_classify_response}
        for article_id, criteria in pre_classify_response.items():
            article = Article.objects.get(pk=int(article_id))
            certain_degree = article.get_certainty_degree(criteria)
            is_selected = certain_degree > 10
            if self.is_test:
                change_value = self.get_change_value(is_selected, article)
                _ = ArticleQualify.objects.create(
                    article=article,
                    qualify_schema=self.qualify_schema,
                    is_selected=is_selected,
                    criteria=criteria,
                    certainty_degree=certain_degree,
                    change_value=change_value,
                    request_id=req_id)
            else:
                article.criteria = criteria
                article.certainty_degree = certain_degree
                article.is_selected = is_selected
                article.save()


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

    def __init__(self, scraper_date: date | str):
        self.scraper_date = date_in_str(scraper_date)
        self.soup_content = get_content(self.main_url(), self.parser)

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
    parser = "html.parser"

    def __init__(self, article: Article, update: bool = False):
        self.article = article
        if article.html_content and not update:
            self.soup_content = BeautifulSoup(
                article.html_content, self.parser)
            self.get_article_data()
            return
        self.soup_content = get_content(article.url, self.parser)
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

    @abstractmethod
    def get_article_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_main_body(self) -> Tag:
        raise NotImplementedError

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
