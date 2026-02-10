from typing import List, Type
from source.models import (
    Article, ScrapedRecord, ArticleQualify, QualifySchema)
from source.base_models import ArticleBase
from source.criteria import BaseCriteriaManager


class FirstCriteriaManager(BaseCriteriaManager):

    def __init__(
            self, recover_record: ScrapedRecord,
            ai_engine: str | None = None, is_test: bool = False
    ) -> None:
        super().__init__(recover_record, ai_engine, is_test)
        self.prompt_name = "first"

    def get_articles_objects(self) -> List[Article]:
        articles = Article.objects.filter(scraped=self.scraped_record)

        if not self.is_test:
            articles = articles.filter(criteria__isnull=True)

        return list(articles)

    def get_schema_class(self, p_count: int) -> Type:
        return ArticleBase

    def pre_process_articles(self, articles: List[Article]) -> List[Article]:
        if self.is_test:
            self.qualify_schema, _ = (
                QualifySchema.objects.get_or_create(
                    scraped_record=self.scraped_record,
                    ia_model=self.ai_engine,
                    prompt_version=self.version,
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
        certain_degree = article.get_certainty_degree_v2(criteria)
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
        saved_is_selected = article_obj.certainty_degree > 100

        if saved_is_selected == is_selected:
            return "selected" if is_selected else "not_selected"

        return "plus" if is_selected else "minus"


