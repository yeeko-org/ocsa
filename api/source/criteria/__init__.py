from abc import ABC, abstractmethod
from typing import List, Type, Any
import json
import enum
from tqdm import tqdm
from source.models import Article, ScrapedRecord, QualifySchema
from utils.gemini_ai import RequestGemini
from source.scraper.articles import CriteriaError
from profile_auth.models import User


class EnumEncoder(json.JSONEncoder):

    def default(self, obj):
        import datetime
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)


class BaseCriteriaManager(ABC):

    classify_request: RequestGemini
    qualify_schema: QualifySchema | None
    prompt_name: str
    user: User | None

    def __init__(
            self, recover_record: ScrapedRecord | None = None,
            ai_engine: str | None = None,
            is_test: bool = False,
            prompt_version: str | None = 'v2'
    ) -> None:
        self.ai_engine: str | None = ai_engine
        self.scraped_record: ScrapedRecord | None = recover_record
        self.is_test = is_test
        self.version = prompt_version
        self.seconds_cache: int = 2

    def add_errors(self, errors: List[str]) -> None:
        saved_errors = self.scraped_record.errors or []
        saved_errors.extend(errors)
        self.scraped_record.errors = saved_errors
        self.scraped_record.save()

    def get_full_content(self, article: Article) -> tuple[str, int]:

        content = f"Título: {article.title.strip()}\n"

        if subtitle := article.subtitle:
            content += f"Subtítulo: {subtitle.strip()}\n"

        p_idx = 0
        for paragraph in article.paragraphs:
            p_idx += 1
            content += f"[{p_idx}]: {paragraph.strip()}\n"

        for photo in article.images or []:
            p_idx += 1
            if caption := photo.get("caption"):
                caption = caption.replace("\n", " ")
                content += f"[{p_idx}]: {caption.strip()} (pie de foto)\n"

        content += self.get_additional_content(article)

        return content, p_idx

    def get_additional_content(self, article: Article) -> str:
        return ""

    def pre_process_articles(self, articles: List[Article]) -> List[Article]:
        return articles

    def build_direct_criteria(self, article: Article) -> None:
        self.build_gemini_request()
        try:
            self.get_ai_criteria(article)
        except CriteriaError as e:
            print("Error building direct criteria:", str(e))
        if self.classify_request.errors:
            print("Request Errors:", self.classify_request.errors)

    def build_criteria(self, articles: List[Article] | None = None):
        if not articles:
            self.scraped_record.set_status(f"{self.prompt_name} criteria")
            articles = self.get_articles_objects()

        articles = self.pre_process_articles(articles)

        self.build_gemini_request(len(articles))

        desc = f"{self.prompt_name} classifying articles"
        for article in tqdm(articles, desc=desc):
            try:
                self.get_ai_criteria(article)
            except CriteriaError as e:
                self.add_errors([str(e)])
                continue

        if self.classify_request.errors:
            self.add_errors(self.classify_request.errors)

    def build_gemini_request(self, len_articles: int = 1) -> None:

        prompt_file = f"gemini_{self.prompt_name}_criteria_{self.version}.txt"
        self.classify_request = RequestGemini(engine=self.ai_engine)
        self.classify_request.build_chat(f"source/prompts/{prompt_file}")

        if len_articles > 1:
            total_seconds_cache = len_articles * self.seconds_cache
            cache_name = f"{self.prompt_name}_criteria_{self.version}"
            self.classify_request.create_cache(cache_name, total_seconds_cache)

    def get_ai_criteria(self, article: Article) -> None:
        if not article.paragraphs and not article.images:
            raise CriteriaError(
                article, "Article has no paragraphs or images")

        full_content, p_count = self.get_full_content(article)
        # full_content = self.prepare_full_content(article, base_content)

        schema_clss = self.get_schema_class(p_count)

        criteria_result = self.classify_request.send_gemini_prompt(
                full_content, schema_clss=schema_clss)

        if not criteria_result:
            raise CriteriaError(article, "No response AI service")

        try:
            criteria = schema_clss.model_validate(criteria_result)
        except Exception as e:
            raise CriteriaError(
                article, f"Response not of class type for {self.prompt_name}", e)

        if not isinstance(criteria, schema_clss):
            msg = f"Invalid response {self.prompt_name}; type: {type(criteria)}"
            raise CriteriaError(article, msg)

        json_criteria = self.get_json_data(criteria)

        self.save_criteria_results(criteria, json_criteria, article)

    def get_json_data(self, criteria: Any) -> dict | list:
        json_criteria = json.dumps(
            criteria.model_dump(), ensure_ascii=False,
            indent=2, cls=EnumEncoder)
        return json.loads(json_criteria)

    @abstractmethod
    def get_articles_objects(self) -> List[Article]:
        raise NotImplementedError

    @abstractmethod
    def get_schema_class(self, p_count: int) -> Type:
        raise NotImplementedError

    # def prepare_full_content(self, article: Article, base_content: str) -> str:
    #     return base_content

    @abstractmethod
    def save_criteria_results(
            self, criteria: Any, json_criteria: dict | list, article: Article):
        raise NotImplementedError
