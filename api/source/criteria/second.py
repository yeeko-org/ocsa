from typing import List, Type, Annotated
import json
from source.models import (
    Article, ScrapedRecord)
from source.base_models import ProjectSelect, ArticleRevision
from source.criteria import BaseCriteriaManager


class SecondCriteriaManager(BaseCriteriaManager):

    prompt_name = "second"
    version = "v2"
    seconds_cache = 3

    def __init__(
            self, recover_record: ScrapedRecord,
            ai_engine: str | None = None, is_test: bool = False,
            prompt_version: str | None = None
    ) -> None:
        super().__init__(
            recover_record, ai_engine, is_test, prompt_version)

    def format_subtitle(self, subtitle: str) -> str:
        return f"Subtítulo: {subtitle.strip()}\n"

    def get_articles_objects(self) -> List[Article]:
        articles = Article.objects.filter(
            scraped=self.scraped_record,
            certainty_degree__gt=100,
            second_criteria__isnull=True
        )
        return list(articles)

    def get_schema_class(self, p_count: int) -> Type[ArticleRevision]:
        from pydantic import Field, BaseModel

        bounded_int = List[Annotated[int, Field(ge=1, le=p_count)]]

        class FeaturesBase(BaseModel):
            opponents: bounded_int
            social_impacts: bounded_int
            ecological_impacts: bounded_int
            acts_of_violence: bounded_int
            collective_actions: bounded_int

        class FinalProjectSelect(FeaturesBase, ProjectSelect):
            paragraphs: bounded_int

        class FinalArticleRevision(ArticleRevision):
            projects: List[FinalProjectSelect]

        return FinalArticleRevision


    def get_additional_content(self, article: Article) -> str:

        additional = (f"\n\n{'=' * 30}\nCriterios y párrafos "
                      f"previamente identificados:\n")

        if article.criteria:
            additional += json.dumps(article.criteria)
        else:
            additional += "No hay criterios previos disponibles."

        return additional

    def post_process_batch(self) -> None:
        from django.utils import timezone

        if not self.scraped_record.date_end:
            self.scraped_record.date_end = timezone.now()
            self.scraped_record.save()

    def save_criteria_results(
            self, criteria: any, json_criteria: dict, article: Article
    ) -> None:

        second_certainty = (article.get_second_certainty_degree(json_criteria))

        sorted_projects = sorted(json_criteria.get("projects", []),
            key=lambda x: x.get("degrees", 0), reverse=True)

        json_criteria["projects"] = sorted_projects
        article.second_criteria = json_criteria
        article.second_certainty_degree = second_certainty
        article.save()
