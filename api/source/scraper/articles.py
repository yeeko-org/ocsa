from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Type
import json
import enum
from tqdm import tqdm
from django.conf import settings
from source.models import (
    Article, ScrapedRecord, Source, ArticleQualify, QualifySchema,
    ArticleBase)
from utils.open_ai import JsonRequestOpenAI
from utils.gemini_ai import RequestGemini
from source.scraper.scraper_base import MainScraper, ArticleScraper

PRECLASSIFY_ARTICLES_BLOCK = getattr(
    settings, "PRECLASSIFY_ARTICLES_BLOCK", 500)


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


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)


class ManagerScraper(ABC):
    scraped_record: ScrapedRecord | None
    main_scraper_class: Type["MainScraper"]
    article_scraper_class: Type["ArticleScraper"]

    date_format = "%Y/%m/%d"
    parser = "html.parser"
    source: Source
    articles_by_date: Dict[str, dict]
    articles_for_ai: list
    articles_by_id: Dict[int, Article]
    overlapping_dates: list
    errors: list
    pre_classify_response: Any
    # pre_classify_request: JsonRequestOpenAI
    pre_classify_request: RequestGemini

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
            print("Overlapping records found, aborting scraping.")
            return

        self.scraped_record = ScrapedRecord.objects.create(
            source=self.get_source(), from_date=date_in_date(from_date),
            to_date=date_in_date(to_date))

    def add_errors(self, errors: List[str]):
        if not self.scraped_record:
            self.errors.extend(errors)
            return
        if not self.scraped_record.errors:
            self.scraped_record.errors = []
        self.scraped_record.errors.extend(errors)
        self.scraped_record.save()

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

        self.articles_for_ai = []
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

        if article_obj.certainty_degree is not None and not reset:
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
        self.articles_for_ai.append(article_for_ai)

    def get_change_value(self, is_selected: bool, article_obj: Article):
        if article_obj.is_selected == is_selected:
            return "selected" if is_selected else "not_selected"
        return "plus" if is_selected else "minus"

    def scrape_articles(self, update: bool = False):
        articles_objects = self.get_articles_objects()
        for article in tqdm(articles_objects, desc="Scraping articles"):
            self.full_scrape_article(article, update)

    def full_scrape_article(
            self, article: Article, update: bool = False):

        if not article.content:
            try:
                article_scraper = self.article_scraper_class(
                    article, update=update)
            except Exception as e:
                self.add_error(
                    f"Error scraping article {article.id}", e)
                return
            try:
                article_scraper.get_reduced_content_text()
            except Exception as e:
                self.add_error(
                    f"Error getting content for article {article.id}", e)

    def build_ai_criteria(
            self, block_size: int = 0, prompt_version: str = "v1"):
        from django.utils import timezone

        self.scraped_record.status = "criteria"
        self.scraped_record.save()
        if block_size:
            self.block_full_articles = block_size
        ready_articles = []
        if self.is_test:
            self.qualify_schema, _ = QualifySchema.objects.get_or_create(
                scraped_record=self.scraped_record,
                ia_model=self.open_ai_engine,
                prompt_version=prompt_version,
                batch_size=self.block_full_articles)
            ready_articles = Article.objects.filter(
                scraped=self.scraped_record,
                qualifications__qualify_schema=self.qualify_schema)\
                .distinct().values_list("id", flat=True)
        else:
            self.qualify_schema = None
        # if self.articles_by_uid:
        # print("articles_by_id:", bool(self.articles_by_id))
        articles_objects = self.get_articles_objects()

        if ready_articles:
            articles_objects = [
                article for article in articles_objects
                if article.id not in ready_articles
            ]
        len_articles = len(articles_objects)
        # print(f"Full scrape articles for {len_articles} articles")

        many_articles = self.block_full_articles > 1
        gemini_text = "prompt_gemini"
        prompt_criteria = (f"{gemini_text}_article{'s' if many_articles else ''}"
                           f"_criteria_{prompt_version}.txt")
        self.pre_classify_request = RequestGemini(engine=self.open_ai_engine)
        cache_multiple = f"multiple_{self.block_full_articles}" \
            if many_articles else "single"
        cache_name = f"criteria_{prompt_version}_{cache_multiple}"
        self.pre_classify_request.build_chat(
            f"source/scraper/{prompt_criteria}")
        seconds_cache = len_articles * 2
        self.pre_classify_request.create_cache(cache_name, seconds_cache)


        desc = f"Classifying articles ({len_articles})"
        article_range = range(0, len_articles, self.block_full_articles)
        for i in tqdm(article_range, desc=desc):
            # init_msg = "Scraping and classifying article"
            # if self.block_full_articles > 1:
            #     print(f"{init_msg}s {i} to {i + self.block_full_articles}")
            # elif i % 10 == 0:
            #     print(f"{init_msg} {i}")
            current_batch = articles_objects[i:i + self.block_full_articles]
            self.get_batch_ai_criteria(
                current_batch, prompt_version=prompt_version)
        if self.pre_classify_request.errors:
            self.add_errors(self.pre_classify_request.errors)
        if not self.scraped_record.date_ended:
            self.scraped_record.date_ended = timezone.now()
            self.scraped_record.save()

    def get_articles_objects(self):
        if self.articles_by_id:
            return list(self.articles_by_id.values())
            # print("type of articles_objects:", type(articles_objects))
        else:
            return list(Article.objects.filter(
                scraped=self.scraped_record, criteria__isnull=True))

    def get_batch_ai_criteria(
            self, articles: List[Article], prompt_version: str = "v1"):
        many_articles = self.block_full_articles > 1
        full_content = ""

        for article in articles:
            if not article.paragraphs and not article.images:
                print(f"Article {article.id} has no paragraphs")
                continue
            p_idx = 0
            content = f"Título: {article.title.strip()}\n"
            if subtitle := article.subtitle:
                content += f"Subtítulo: {subtitle.strip()}\n"
            for paragraph in article.paragraphs:
                p_idx += 1
                content += f"[{p_idx}]: {paragraph.strip()}\n"
            # if p_idx >= 89:
            #     print(f"Article {article.id} has too many paragraphs: {p_idx}")
            # else:
            #     p_idx = 89
            for photo in article.images or []:
                p_idx += 1
                if caption := photo.get("caption"):
                    caption = caption.replace("\n", " ")
                    content += f"[{p_idx}]: {caption.strip()} (pie de foto)\n"

            if many_articles:
                full_content += f"-- ARTÍCULO id: {article.id} --\n\n{content}\n\n\n"
            else:
                full_content = content
        if not full_content:
            print("No content to classify")
            return

        pre_classify_response = self.pre_classify_request\
            .send_gemini_prompt(full_content, schema_clss=ArticleBase)

        if not pre_classify_response:
            print("No response from OpenAI")
            return

        if not isinstance(pre_classify_response, ArticleBase):
            print(f"Invalid response, received: {type(pre_classify_response)}")
            return
        if not many_articles:
            pre_classify_response = [pre_classify_response]
        for criteria in pre_classify_response:
            if not many_articles:
                article_id = articles[0].id
            else:
                article_id = criteria.id
            article = Article.objects.get(pk=int(article_id))
            certain_degree = article.get_certainty_degree_v2(criteria)
            is_selected = certain_degree > 100
            if self.is_test:
                change_value = self.get_change_value(is_selected, article)
                _ = ArticleQualify.objects.create(
                    article=article,
                    qualify_schema=self.qualify_schema,
                    is_selected=is_selected,
                    criteria=criteria,
                    certainty_degree=certain_degree,
                    change_value=change_value,
                    request_id=None)
            else:
                json_criteria = json.dumps(
                    criteria.model_dump(), ensure_ascii=False,
                    indent=2, cls=EnumEncoder)
                article.criteria = json.loads(json_criteria)
                article.certainty_degree = certain_degree
                # article.is_selected = is_selected
                article.save()
