from abc import ABC, abstractmethod
from typing import List, Type, Any, Protocol
import json
import enum
from tqdm import tqdm
from source.models import Article, ScrapedRecord, QualifySchema
from utils.gemini_ai import (
    RequestGemini, MIN_PENDING_FOR_CACHE, MAX_FAILED_STREAK)
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


class GeminiPromptOwner(Protocol):
    """Atributos que ``make_gemini_request`` lee del caller."""
    prompt_name: str
    version: str | None
    ai_engine: str | None
    seconds_cache: int


def make_gemini_request(
        owner: GeminiPromptOwner, len_articles: int = 1,
        prompt_segment: str = "criteria", extra_system: str = "",
) -> RequestGemini:
    """Construye un ``RequestGemini`` listo (chat + cache opcional).

    ``prompt_segment`` permite reutilizar este helper en flujos que no
    son clasificación (p. ej. ``pdf_cleanup`` pasa ``""``).

    ``extra_system`` se concatena al ``system_msg`` antes de crear el
    caché, porque ``create_cache`` congela el system_instruction: lo que
    llegue después ya no viaja en las llamadas cacheadas.
    """
    seg = f"_{prompt_segment}" if prompt_segment else ""
    prompt_file = f"gemini_{owner.prompt_name}{seg}_{owner.version}.txt"
    request = RequestGemini(engine=owner.ai_engine)
    request.build_chat(f"source/prompts/{prompt_file}")
    if extra_system:
        request.system_msg += f"\n\n{extra_system}"
    if len_articles > 1:
        total = len_articles * owner.seconds_cache
        cache_name = f"{owner.prompt_name}{seg}_{owner.version}"
        request.create_cache(cache_name, total)
    return request


class BaseCriteriaManager(ABC):

    classify_request: RequestGemini
    qualify_schema: QualifySchema | None
    user: User | None

    # Cada subclase declara los suyos: sin default global, dos flujos no
    # pueden quedarse con versiones distintas del prompt sin que se note.
    prompt_name: str
    version: str = ""
    seconds_cache: int = 2

    def __init__(
            self, recover_record: ScrapedRecord | None = None,
            ai_engine: str | None = None,
            is_test: bool = False,
            prompt_version: str | None = None
    ) -> None:
        self.ai_engine: str | None = ai_engine
        self.scraped_record: ScrapedRecord | None = recover_record
        self.is_test = is_test
        if prompt_version:
            self.version = prompt_version
        if not self.version:
            raise ValueError(
                f"{type(self).__name__} debe declarar `version`")

    def add_errors(self, errors: List[str]) -> None:
        # Los flujos sin lote (p. ej. `reclassify_legal`) no tienen dónde
        # guardarlos, pero sí deben poder reportarlos.
        if not self.scraped_record:
            for error in errors:
                print(error)
            return
        saved_errors = self.scraped_record.errors or []
        saved_errors.extend(errors)
        self.scraped_record.errors = saved_errors
        self.scraped_record.save()

    def format_subtitle(self, subtitle: str) -> str:
        """Línea del subtítulo. No consume índice de párrafo.

        Las pasadas `first` y `second` lo emiten sin numerar: su esquema
        acota las referencias a `ge=1` y un `[0]` en la respuesta rompe
        la validación.
        """
        return f"[0]: {subtitle.strip()} (subtítulo)\n"

    def get_full_content(self, article: Article) -> tuple[str, int]:

        content = f"Título: {article.title.strip()}\n"

        if subtitle := article.subtitle:
            content += self.format_subtitle(subtitle)

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

    def get_extra_system_msg(self) -> str:
        """Bloque que se añade al system_msg antes de crear el caché."""
        return ""

    def pre_process_articles(self, articles: List[Article]) -> List[Article]:
        return articles

    def post_process_batch(self) -> None:
        """Cierre del lote, tras recorrer todos los artículos."""
        return None

    def build_direct_criteria(self, article: Article) -> None:
        self.build_gemini_request()
        try:
            self.get_ai_criteria(article)
        except CriteriaError as e:
            print("Error building direct criteria:", str(e))
        if self.classify_request.errors:
            print("Request Errors:", self.classify_request.errors)

    def build_criteria(self, articles: List[Article] | None = None):
        if articles is None:
            articles = self.get_articles_objects()

        articles = self.pre_process_articles(articles)
        if not articles:
            print(f"{self.prompt_name}: nada que clasificar")
            self.post_process_batch()
            return

        len_articles = len(articles)
        self.build_gemini_request(len_articles)
        if self.classify_request.cache_error:
            self.add_errors([self.classify_request.cache_error])

        desc = f"{self.prompt_name} classifying articles"
        failed_streak = 0
        last_status = None
        for idx, article in enumerate(tqdm(articles, desc=desc)):
            try:
                self.get_ai_criteria(article)
            except CriteriaError as e:
                failed_streak = (
                    failed_streak + 1 if e.status == last_status else 1)
                last_status = e.status
                if failed_streak >= MAX_FAILED_STREAK:
                    self.abort_batch(failed_streak, last_status)
                    break
                if self.classify_request.cache_lost:
                    self.recover_cache(len_articles - idx - 1)
                continue
            failed_streak = 0
            last_status = None

        if self.classify_request.errors:
            print("Request errors:", self.classify_request.errors)
        self.post_process_batch()

    def abort_batch(self, streak: int, status: str) -> None:
        msg = f"Lote abortado tras {streak} fallos seguidos por: {status}"
        self.add_errors([msg])
        print(msg)

    def recover_cache(self, pending: int) -> None:
        """Rehace el caché expirado si aún quedan artículos que lo amorticen.

        Al no recrearlo el lote no muere: sigue con el system_instruction
        inline, que cuesta más tokens pero clasifica igual.
        """
        request = self.classify_request
        if pending < MIN_PENDING_FOR_CACHE:
            request.cache = None
            return
        # Solo se reporta la transición a inline: repetirlo por cada artículo
        # posterior volvería a llenar ScrapedRecord.errors de ruido.
        was_disabled = request.cache_disabled
        if request.recreate_cache() or was_disabled:
            return
        self.add_errors([
            request.cache_error
            or "Caché perdido y sin reintentos; el lote sigue inline"])

    def build_gemini_request(self, len_articles: int = 1) -> None:
        self.classify_request = make_gemini_request(
            self, len_articles, extra_system=self.get_extra_system_msg())

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
            raise CriteriaError(
                article, "No response AI service",
                cause=self.classify_request.last_error,
                status=self.classify_request.last_status)

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
