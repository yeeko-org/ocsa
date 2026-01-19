from abc import ABC
from typing import List, Type, Annotated
import json
import enum
from tqdm import tqdm
from source.models import (
    Article, ScrapedRecord, ArticleQualify, QualifySchema,
    ArticleBase, ArticleRevision, ProjectSelect)
from utils.gemini_ai import RequestGemini
from source.scraper.articles import CriteriaError


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)


class ManagerCriteria:
    scraped_record: ScrapedRecord | None
    classify_request: RequestGemini
    ai_engine: str | None
    qualify_schema: QualifySchema | None

    def __init__(
            self, recover_record: ScrapedRecord,
            ai_engine: str | None = None, is_test: bool = False
    ) -> None:
        self.ai_engine = ai_engine
        self.scraped_record = recover_record
        self.is_test = is_test

    def add_errors(self, errors: List[str]):
        saved_errors = self.scraped_record.errors or []
        saved_errors.extend(errors)
        self.scraped_record.errors = saved_errors
        self.scraped_record.save()

    def build_gemini_request(
            self,
            prompt_name: str,
            prompt_version: str,
            articles: List[Article] | None = None,
            seconds_cache: int = 3
    ):
        self.scraped_record.set_status(f"{prompt_name} criteria")
        is_second = "second" in prompt_name.lower()
        print("is_second:", is_second)
        if not articles:
            articles = self.get_articles_objects(is_second=is_second)
        if not is_second:
            articles = self.test_qualify_schema(
                prompt_version=prompt_version, articles=articles)
        len_articles = len(articles)
        prompt_file = f"gemini_{prompt_name}_criteria_{prompt_version}.txt"
        total_seconds_cache = len_articles * seconds_cache
        self.classify_request = RequestGemini(engine=self.ai_engine)
        self.classify_request.build_chat(f"source/prompts/{prompt_file}")
        cache_name = f"{prompt_name}_criteria_{prompt_version}"
        self.classify_request.create_cache(cache_name, total_seconds_cache)

        desc = f"{prompt_name} classifying articles ({len_articles})"
        for article in tqdm(articles, desc=desc):
            try:
                self.get_ai_criteria(article, is_second=is_second)
            except CriteriaError as e:
                self.add_errors([str(e)])
                continue
        if self.classify_request.errors:
            self.add_errors(self.classify_request.errors)

    def test_qualify_schema(
            self, prompt_version: str = "v2",
            articles: List[Article] | None = None):

        if self.is_test:
            self.qualify_schema, _ = QualifySchema.objects.get_or_create(
                scraped_record=self.scraped_record,
                ia_model=self.ai_engine,
                prompt_version=prompt_version,
                batch_size=1)
            ready_articles = Article.objects.filter(
                scraped=self.scraped_record,
                qualifications__qualify_schema=self.qualify_schema) \
                .distinct().values_list("id", flat=True)

            articles = [
                article for article in articles
                if article.id not in ready_articles
            ]

        else:
            self.qualify_schema = None
        return articles

    def build_first_criteria(
            self, prompt_version: str = "v2",
            articles: List[Article] | None = None):

        self.build_gemini_request(
            prompt_name="first",
            prompt_version=prompt_version,
            articles=articles,
            seconds_cache=2
        )

    def get_articles_objects(
            self, is_second: bool = False
    ) -> List[Article]:
        articles = Article.objects.filter(scraped=self.scraped_record)
        if not self.is_test and not is_second:
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

    def get_ai_criteria(self, article: Article, is_second: bool = False):

        if not article.paragraphs and not article.images:
            raise CriteriaError(
                article, "Article has no paragraphs or images")

        full_content, p_count = self.get_full_content(article)
        prompt_name = "second" if is_second else "first"

        if is_second:
            full_content += (f"\n\n{'=' * 30}\nCriterios y párrafos "
                             f"previamente identificados:\n")
            if article.criteria:
                full_content += json.dumps(article.criteria)
            else:
                full_content += "No hay criterios previos disponibles."
            schema_clss = self.build_article_revision_class(p_count)
        else:
            schema_clss = ArticleBase

        criteria_result = self.classify_request \
            .send_gemini_prompt(full_content, schema_clss=schema_clss)

        if not criteria_result:
            raise CriteriaError(article, "No response AI service")

        try:
            criteria = schema_clss.model_validate(criteria_result)
        except Exception as e:
            raise CriteriaError(
                article,
                f"Response not of class type for {prompt_name}", e)

        if not isinstance(criteria, schema_clss):
            msg = f"Invalid response {prompt_name}; type: {type(criteria)}"
            raise CriteriaError(article, msg)

        json_criteria = json.dumps(
            criteria.model_dump(), ensure_ascii=False,
            indent=2, cls=EnumEncoder)
        json_criteria = json.loads(json_criteria)

        if is_second:
            self.save_second_criteria_results(json_criteria, article)
        else:
            self.save_first_criteria_results(criteria, json_criteria, article)

    def save_first_criteria_results(
            self, criteria: ArticleBase, json_criteria: dict, article: Article):

        certain_degree = article.get_certainty_degree_v2(criteria)
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

    def save_second_criteria_results(
            self, json_criteria: dict, article: Article):

        second_certainty = article.get_second_certainty_degree(json_criteria)
        sorted_projects = sorted(
            json_criteria.get("projects", []),
            key=lambda x: x.get("degrees", 0), reverse=True)
        json_criteria["projects"] = sorted_projects
        article.second_criteria = json_criteria
        article.second_certainty_degree = second_certainty
        article.save()

    def get_change_value(self, is_selected: bool, article_obj: Article):
        saved_is_selected = article_obj.certainty_degree > 100
        if saved_is_selected == is_selected:
            return "selected" if is_selected else "not_selected"
        return "plus" if is_selected else "minus"

    def build_second_criteria(
            self, prompt_version: str = "v2",
            articles: List[Article] | None = None):
        from django.utils import timezone

        self.build_gemini_request(
            prompt_name="second",
            prompt_version=prompt_version,
            articles=articles,
            seconds_cache=3
        )

        if not self.scraped_record.date_end:
            self.scraped_record.date_end = timezone.now()
            self.scraped_record.save()

    def build_article_revision_class(
            self, p_count: int
    ) -> Type[ArticleRevision]:

        features_base, bounded_int = self.build_features_base_class(p_count)

        class FinalProjectSelect(features_base, ProjectSelect):
            paragraphs: bounded_int

        class FinalArticleRevision(ArticleRevision):
            projects: List[FinalProjectSelect]

        return FinalArticleRevision

    def build_features_base_class(self, p_count: int):
        from pydantic import Field, BaseModel

        bounded_int = List[Annotated[int, Field(ge=1, le=p_count)]]

        class FeaturesBase(BaseModel):
            opponents: bounded_int
            social_impacts: bounded_int
            ecological_impacts: bounded_int
            acts_of_violence: bounded_int
            collective_actions: bounded_int

        return FeaturesBase, bounded_int
