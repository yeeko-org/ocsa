from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Type
import json
import enum
from tqdm import tqdm
from django.conf import settings
from source.models import (
    Article, ScrapedRecord, Source, ArticleQualify, QualifySchema,
    ArticleBase, ArticleRevision, ProjectBase, ProjectSelect)
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


class CriteriaError(Exception):

    def __init__(self, article: Article, message: str,
                 exception: Exception | None = None):
        from django.utils import timezone
        final_msg = message
        if exception:
            final_msg += f" | Exception: {str(exception)}"
        if article:
            article_error = f"{timezone.now().isoformat()} - {final_msg}"
            article.errors = article.errors or []
            article.errors.append(article_error)
            article.save()
        final_msg = f"ID - {article.id} ({article.title}): {final_msg}"
        super().__init__(final_msg)


class ManagerScraper(ABC):
    scraped_record: ScrapedRecord | None
    main_scraper_class: Type["MainScraper"]
    article_scraper_class: Type["ArticleScraper"]

    date_format = "%Y/%m/%d"
    parser = "html.parser"
    source: Source
    articles_by_date: Dict[str, dict]
    # articles_for_ai: list
    articles_by_id: Dict[int, Article]
    overlapping_dates: list
    errors: list
    pre_classify_response: Any
    # pre_classify_request: JsonRequestOpenAI
    pre_classify_request: RequestGemini

    second_classify_response: Any
    second_classify_request: RequestGemini

    ai_engine: str | None
    # use_deepseek: bool
    qualify_schema: QualifySchema | None

    def __init__(
            self, from_date: str | date | None, to_date: str | date | None,
            main_scraper_class: Type["MainScraper"],
            article_scraper_class: Type["ArticleScraper"],
            recover_record: ScrapedRecord | None = None,
            ai_engine: str | None = None,
            is_test: bool = False

    ) -> None:
        self.block_size = PRECLASSIFY_ARTICLES_BLOCK
        self.main_scraper_class = main_scraper_class
        self.article_scraper_class = article_scraper_class
        self.overlapping_dates = []
        self.articles_by_id = {}
        # self.first_selected_articles: List[Article] = []
        self.errors = []
        self.ai_engine = ai_engine
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

    def add_error(
            self, error: str,
            exception: Exception | None = None,
            raise_exception: bool = False):

        if exception and raise_exception:
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

        # self.articles_for_ai = []
        self.articles_by_id = {}
        self.get_source()
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

        # if not title:
        #     return
        #
        # article_for_ai = {
        #     "id": article_id,
        #     "title": title,
        #     "section": section_name,
        # }
        # if content:
        #     article_for_ai["content"] = content
        # self.articles_for_ai.append(article_for_ai)

    def get_change_value(self, is_selected: bool, article_obj: Article):
        saved_is_selected = article_obj.certainty_degree > 100
        if saved_is_selected == is_selected:
            return "selected" if is_selected else "not_selected"
        return "plus" if is_selected else "minus"

    def scrape_articles(self, update: bool = False):
        articles_objects = self.get_articles_objects()
        for article in tqdm(articles_objects, desc="Scraping articles"):
            try:
                self.full_scrape_article(article, update)
            except CriteriaError as e:
                self.add_error(str(e))

    def full_scrape_article(
            self, article: Article, update: bool = False):

        if not article.content:
            try:
                article_scraper = self.article_scraper_class(
                    article, update=update)
            except Exception as e:
                raise CriteriaError(
                    article, "Error scraping article", e)
            try:
                article_scraper.get_reduced_content_text()
            except Exception as e:
                raise CriteriaError(
                    article, "Error getting content for article", e)

    def build_ai_criteria(self, prompt_version: str = "v2"):
        self.scraped_record.status = "criteria"
        self.scraped_record.save()
        articles_objects: List[Article] = self.get_articles_objects()
        if self.is_test:
            self.qualify_schema, _ = QualifySchema.objects.get_or_create(
                scraped_record=self.scraped_record,
                ia_model=self.ai_engine,
                prompt_version=prompt_version,
                batch_size=1)
            ready_articles = Article.objects.filter(
                scraped=self.scraped_record,
                qualifications__qualify_schema=self.qualify_schema)\
                .distinct().values_list("id", flat=True)

            articles_objects = [
                article for article in articles_objects
                if article.id not in ready_articles
            ]

        else:
            self.qualify_schema = None

        len_articles = len(articles_objects)

        gemini_text = "prompt_gemini"
        prompt_criteria = (f"{gemini_text}_article"
                           f"_criteria_{prompt_version}.txt")
        self.pre_classify_request = RequestGemini(engine=self.ai_engine)
        cache_name = f"criteria_{prompt_version}_single"
        self.pre_classify_request.build_chat(
            f"source/scraper/{prompt_criteria}")
        seconds_cache = len_articles * 3
        self.pre_classify_request.create_cache(cache_name, seconds_cache)

        desc = f"Classifying articles ({len_articles})"
        for article in tqdm(articles_objects, desc=desc):
            try:
                self.get_ai_criteria(article)
            except CriteriaError as e:
                self.add_error(str(e))
                continue
        if self.pre_classify_request.errors:
            self.add_errors(self.pre_classify_request.errors)

        # self.build_second_criteria(prompt_version=prompt_version)

    def get_articles_objects(
            self, is_second: bool = False
    ) -> List[Article]:
        if self.articles_by_id:
            return list(self.articles_by_id.values())
            # print("type of articles_objects:", type(articles_objects))
        else:
            articles = Article.objects.filter(scraped=self.scraped_record)
            if not self.is_test:
                articles = articles.filter(criteria__isnull=True)
            if is_second:
                articles = articles.filter(
                    certainty_degree__gt=100,
                    second_criteria__isnull=True)
            return list(articles)

    def get_full_content(self, article: Article) -> tuple[str, int]:
        p_idx = 0
        content = f"Título: {article.title.strip()}\n"
        if subtitle := article.subtitle:
            content += f"Subtítulo: {subtitle.strip()}\n"

        for paragraph in article.paragraphs:
            p_idx += 1
            content += f"[{p_idx}]: {paragraph.strip()}\n"

        for photo in article.images or []:
            p_idx += 1
            if caption := photo.get("caption"):
                caption = caption.replace("\n", " ")
                content += f"[{p_idx}]: {caption.strip()} (pie de foto)\n"

        return content, p_idx

    def get_ai_criteria(self, article: Article):

        if not article.paragraphs and not article.images:
            raise CriteriaError(
                article, "Article has no paragraphs or images")

        full_content, p_count = self.get_full_content(article)

        schema_clss = self.build_article_base_class(p_count)
        criteria = self.pre_classify_request\
            .send_gemini_prompt(full_content, schema_clss=schema_clss)

        if not criteria:
            raise CriteriaError(article, "No response AI service")

        criteria = schema_clss.model_validate(criteria)

        if not isinstance(criteria, schema_clss):
            msg = f"Invalid response type; type: {type(criteria)}"
            raise CriteriaError(article, msg)

        self.save_criteria_results(criteria, article.id)

    def build_features_base_class(self, p_count: int):
        from pydantic import Field, BaseModel
        from typing import Annotated, List

        bounded_int = List[Annotated[int, Field(ge=1, le=p_count)]]

        class FeaturesBase(BaseModel):
            opponents: bounded_int
            social_impacts: bounded_int
            ecological_impacts: bounded_int
            acts_of_violence: bounded_int
            collective_actions: bounded_int

        return FeaturesBase, bounded_int

    def build_article_base_class(self, p_count: int) -> Type[ArticleBase]:
        from typing import List

        features_base, bounded_int = self.build_features_base_class(p_count)

        class FinalProjectBase(ProjectBase):
            paragraphs: bounded_int

        class FinalArticleBase(ArticleBase, features_base):
            projects: List[FinalProjectBase]

        return FinalArticleBase

    def save_criteria_results(
            self, criteria:type[ArticleBase], article_id: int):
        article = Article.objects.get(pk=int(article_id))
        certain_degree = article.get_certainty_degree_v2(criteria)
        json_criteria = json.dumps(
            criteria.model_dump(), ensure_ascii=False,
            indent=2, cls=EnumEncoder)
        json_criteria = json.loads(json_criteria)
        is_pre_selected = certain_degree > 100
        if self.is_test:
            change_value = self.get_change_value(is_pre_selected, article)
            _ = ArticleQualify.objects.create(
                article=article,
                qualify_schema=self.qualify_schema,
                criteria=json_criteria,
                certainty_degree=certain_degree,
                change_value=change_value,
                request_id=None)
        else:
            article.criteria = json_criteria
            article.certainty_degree = certain_degree
            article.save()

        return is_pre_selected

    def build_second_criteria(
            self, prompt_version: str = "v2",
            articles: List[Article] | None = None):
        from django.utils import timezone

        prompt_criteria = f"gemini_second_criteria_{prompt_version}.txt"
        self.second_classify_request = RequestGemini(engine=self.ai_engine)
        cache_name = f"second:criteria_{prompt_version}"
        self.second_classify_request.build_chat(
            f"source/prompts/{prompt_criteria}")
        if not articles:
            articles = self.get_articles_objects(is_second=True)
        len_articles = len(articles)

        seconds_cache = len_articles * 3
        self.second_classify_request.create_cache(cache_name, seconds_cache)

        desc = f"Reclassifying articles ({len_articles})"
        for article in tqdm(articles, desc=desc):
            try:
                self.send_second_criteria(article)
            except CriteriaError as e:
                self.add_error(str(e))
                continue
        if self.second_classify_request.errors:
            self.add_errors(self.second_classify_request.errors)
        if not self.scraped_record.date_end:
            self.scraped_record.date_end = timezone.now()
            self.scraped_record.save()

    def save_second_criteria(
            self, criteria:Type[ArticleRevision], article: Article):

        json_criteria = json.dumps(
            criteria.model_dump(), ensure_ascii=False,
            indent=2, cls=EnumEncoder)
        json_criteria = json.loads(json_criteria)
        second_certainty = article.get_second_certainty_degree(json_criteria)
        # sort json_criteria projects by "degrees" descending
        sorted_projects = sorted(
            json_criteria.get("projects", []),
            key=lambda x: x.get("degrees", 0), reverse=True)
        json_criteria["projects"] = sorted_projects
        article.second_criteria = json_criteria

        article.second_certainty_degree = second_certainty
        article.save()

    def send_second_criteria(self, article: Article):

        full_content, p_count = self.get_full_content(article)
        full_content += f"\n\n{'='*30}\nCriterios y párrafos previamente identificados:\n"
        if article.criteria:
            full_content += json.dumps(
                article.criteria, ensure_ascii=False,
                indent=2, cls=EnumEncoder)
        else:
            full_content += "No hay criterios previos disponibles."
        schema_clss = self.build_article_revision_class(p_count)
        second_criteria = self.second_classify_request\
            .send_gemini_prompt(full_content, schema_clss=schema_clss)
        try:
            second_criteria = schema_clss.model_validate(second_criteria)
        except Exception as e:
            raise CriteriaError(
                article,
                "Response not of class type ArticleRevision", e)
        if not second_criteria or not isinstance(second_criteria, schema_clss):
            raise CriteriaError(
                article,
                "Invalid second criteria response from AI service")

        self.save_second_criteria(second_criteria, article)

    def build_article_revision_class(
            self, p_count: int
    ) -> Type[ArticleRevision]:

        from typing import List

        features_base, bounded_int = self.build_features_base_class(p_count)

        class FinalProjectSelect(features_base, ProjectSelect):
            paragraphs: bounded_int

        class FinalArticleRevision(ArticleRevision):
            projects: List[FinalProjectSelect]

        return FinalArticleRevision