from abc import ABC, abstractmethod
from typing import List, Type, Annotated, Any
import json
import enum
from tqdm import tqdm
from source.models import (
    Article, ScrapedRecord, ArticleQualify, QualifySchema,
    ArticleBase, ArticleRevision, ProjectSelect
)
from utils.gemini_ai import RequestGemini
from source.scraper.articles import CriteriaError


class EnumEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)


class BaseCriteriaManager(ABC):

    scraped_record: ScrapedRecord | None
    classify_request: RequestGemini
    ai_engine: str | None
    qualify_schema: QualifySchema | None

    def __init__(
            self,
            recover_record: ScrapedRecord,
            ai_engine: str | None = None,
            is_test: bool = False
    ) -> None:
        self.ai_engine = ai_engine
        self.scraped_record = recover_record
        self.is_test = is_test

    def build_criteria(
            self, prompt_version: str | None = None,
            articles: List[Article] | None = None
    ) -> None:
        if prompt_version is None:
            prompt_version = self.get_prompt_version_default()

        self.build_gemini_request(prompt_version, articles)

    @abstractmethod
    def get_prompt_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_prompt_version_default(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_seconds_cache(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_articles_objects(self) -> List[Article]:
        raise NotImplementedError

    @abstractmethod
    def get_schema_class(self, article: Article, p_count: int) -> Type:
        raise NotImplementedError

    def prepare_full_content(self, article: Article, base_content: str) -> str:
        return base_content

    @abstractmethod
    def save_criteria_results(
            self, criteria: Any, json_criteria: dict, article: Article):
        raise NotImplementedError

    def add_errors(self, errors: List[str]) -> None:
        saved_errors = self.scraped_record.errors or []
        saved_errors.extend(errors)
        self.scraped_record.errors = saved_errors
        self.scraped_record.save()

    def get_full_content(
            self, article: Article
    ) -> tuple[str, int]:
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

    def pre_process_articles(
            self, prompt_version: str, articles: List[Article]
    ) -> List[Article]:
        return articles

    def build_gemini_request(
            self, prompt_version: str, articles: List[Article] | None = None):
        prompt_name = self.get_prompt_name()
        self.scraped_record.set_status(f"{prompt_name} criteria")

        if not articles:
            articles = self.get_articles_objects()

        articles = self.pre_process_articles(prompt_version, articles)

        len_articles = len(articles)
        prompt_file = f"gemini_{prompt_name}_criteria_{prompt_version}.txt"

        seconds_cache = self.get_seconds_cache()
        total_seconds_cache = len_articles * seconds_cache

        self.classify_request = RequestGemini(
            engine=self.ai_engine
        )
        self.classify_request.build_chat(
            f"source/prompts/{prompt_file}"
        )

        cache_name = f"{prompt_name}_criteria_{prompt_version}"
        self.classify_request.create_cache(cache_name, total_seconds_cache)

        desc = f"{prompt_name} classifying articles ({len_articles})"

        for article in tqdm(articles, desc=desc):
            try:
                self.get_ai_criteria(article)
            except CriteriaError as e:
                self.add_errors([str(e)])
                continue

        if self.classify_request.errors:
            self.add_errors(self.classify_request.errors)

    def get_ai_criteria(self, article: Article) -> None:
        if not article.paragraphs and not article.images:
            raise CriteriaError(
                article, "Article has no paragraphs or images")

        base_content, p_count = self.get_full_content(article)
        full_content = self.prepare_full_content(article, base_content)

        schema_clss = self.get_schema_class(article, p_count)

        criteria_result = self.classify_request.send_gemini_prompt(
                full_content, schema_clss=schema_clss)

        if not criteria_result:
            raise CriteriaError(article, "No response AI service")

        try:
            criteria = schema_clss.model_validate(criteria_result)
        except Exception as e:
            prompt_name = self.get_prompt_name()
            raise CriteriaError(
                article, f"Response not of class type for {prompt_name}", e)

        if not isinstance(criteria, schema_clss):
            prompt_name = self.get_prompt_name()
            msg = f"Invalid response {prompt_name}; type: {type(criteria)}"
            raise CriteriaError(article, msg)

        json_criteria = json.dumps(
            criteria.model_dump(), ensure_ascii=False,
            indent=2, cls=EnumEncoder)
        json_criteria = json.loads(json_criteria)

        self.save_criteria_results(criteria, json_criteria, article)
