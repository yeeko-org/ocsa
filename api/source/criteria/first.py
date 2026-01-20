from abc import ABC, abstractmethod
from typing import List, Type, Annotated
import json
import enum
from tqdm import tqdm
from source.models import (
    Article, ScrapedRecord, ArticleQualify, QualifySchema,
    ArticleBase, ArticleRevision, ProjectSelect
)
from utils.gemini_ai import RequestGemini
from source.scraper.articles import CriteriaError
from source.criteria import BaseCriteriaManager


class FirstCriteriaManager(BaseCriteriaManager):

    def get_prompt_name(self) -> str:
        return "first"

    def get_prompt_version_default(self) -> str:
        return "v2"

    def get_seconds_cache(self) -> int:
        return 2

    def get_articles_objects(self) -> List[Article]:
        articles = Article.objects.filter(scraped=self.scraped_record)

        if not self.is_test:
            articles = articles.filter(criteria__isnull=True)

        return list(articles)

    def get_schema_class(self, article: Article, p_count: int) -> Type:
        return ArticleBase

    def pre_process_articles(
            self, prompt_version: str,
            articles: List[Article]
    ) -> List[Article]:
        if self.is_test:
            self.qualify_schema, _ = (
                QualifySchema.objects.get_or_create(
                    scraped_record=self.scraped_record,
                    ia_model=self.ai_engine,
                    prompt_version=prompt_version,
                    batch_size=1
                )
            )

            ready_articles = Article.objects.filter(
                scraped=self.scraped_record,
                qualifications__qualify_schema=(
                    self.qualify_schema
                )
            ).distinct().values_list("id", flat=True)

            articles = [
                article for article in articles
                if article.id not in ready_articles
            ]
        else:
            self.qualify_schema = None

        return articles

    def save_criteria_results(
            self, criteria: ArticleBase,
            json_criteria: dict, article: Article
    ) -> None:
        certain_degree = (
            article.get_certainty_degree_v2(criteria)
        )
        is_pre_selected = certain_degree > 100

        if self.is_test:
            change_value = self._get_change_value(
                is_pre_selected, article
            )
            _ = ArticleQualify.objects.create(
                article=article,
                qualify_schema=self.qualify_schema,
                criteria=json_criteria,
                certainty_degree=certain_degree,
                change_value=change_value,
                request_id=None
            )
        else:
            article.criteria = json_criteria
            article.certainty_degree = certain_degree
            article.save()

    def _get_change_value(
            self, is_selected: bool, article_obj: Article
    ) -> str:
        saved_is_selected = (
                article_obj.certainty_degree > 100
        )

        if saved_is_selected == is_selected:
            return (
                "selected" if is_selected
                else "not_selected"
            )

        return "plus" if is_selected else "minus"


class SecondCriteriaManager(BaseCriteriaManager):
    """Manager for second criteria evaluation."""

    def get_prompt_name(self) -> str:
        return "second"

    def get_prompt_version_default(self) -> str:
        return "v2"

    def get_seconds_cache(self) -> int:
        return 3

    def get_articles_objects(self) -> List[Article]:
        articles = Article.objects.filter(
            scraped=self.scraped_record,
            certainty_degree__gt=100,
            second_criteria__isnull=True
        )
        return list(articles)

    def get_schema_class(
            self, article: Article, p_count: int
    ) -> Type:
        return self._build_article_revision_class(
            p_count
        )

    def prepare_full_content(self, article: Article, base_content: str) -> str:
        additional = (
            f"\n\n{'=' * 30}\n Criterios y párrafos "
            f"previamente identificados:\n"
        )

        if article.criteria:
            additional += json.dumps(article.criteria)
        else:
            additional += "No hay criterios previos disponibles."

        return base_content + additional

    def save_criteria_results(
            self, criteria: any, json_criteria: dict,
            article: Article
    ) -> None:
        second_certainty = (
            article.get_second_certainty_degree(
                json_criteria
            )
        )

        sorted_projects = sorted(
            json_criteria.get("projects", []),
            key=lambda x: x.get("degrees", 0),
            reverse=True
        )

        json_criteria["projects"] = sorted_projects
        article.second_criteria = json_criteria
        article.second_certainty_degree = second_certainty
        article.save()

    def build_criteria(
            self,
            prompt_version: str | None = None,
            articles: List[Article] | None = None
    ) -> None:
        from django.utils import timezone

        super().build_criteria(prompt_version, articles)

        if not self.scraped_record.date_end:
            self.scraped_record.date_end = timezone.now()
            self.scraped_record.save()

    def _build_article_revision_class(
            self, p_count: int) -> Type[ArticleRevision]:
        from pydantic import Field, BaseModel

        bounded_int = List[
            Annotated[int, Field(ge=1, le=p_count)]
        ]

        class FeaturesBase(BaseModel):
            opponents: bounded_int
            social_impacts: bounded_int
            ecological_impacts: bounded_int
            acts_of_violence: bounded_int
            collective_actions: bounded_int

        class FinalProjectSelect(
            FeaturesBase, ProjectSelect
        ):
            paragraphs: bounded_int

        class FinalArticleRevision(ArticleRevision):
            projects: List[FinalProjectSelect]

        return FinalArticleRevision