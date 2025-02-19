# Ejecucion de pruebas de scraping por pasos completos, y sus formas de ver la informacion.

from pprint import pprint
from source.scraper.jornada import JornadaManagerScraper
from source.models import (
    ScrapedRecord, Article, QualifySchema, ArticleQualify)

manager_scraper = JornadaManagerScraper(
    "2022/07/01", "2022/07/25", open_ai_engine="gpt-4o-mini")

# print(manager_scraper.scraped_record)
manager_scraper.scrape_sections()

manager_scraper = JornadaManagerScraper(
    "", "", recover_record=ScrapedRecord.objects.get(pk=19),
    open_ai_engine="gpt-4o-mini")

manager_scraper = JornadaManagerScraper(
    "", "", recover_record=ScrapedRecord.objects.last(),
    open_ai_engine="gpt-4o-mini")

manager_scraper.record_articles(reset=True)

manager_scraper.full_scrape_articles(
    all_articles=True, block_size=1, prompt_version="v2")

# QualifySchema.objects.all().delete()
Article.objects.filter(scraped__id=18).count()

########

# python manage.py articles_json "2022-03-01" "2022-03-28" 4
# python manage.py compare_notes --settings=core.settings_prod
########


def preclassify_articles(
        block_size=500, sr_id=17, open_ai_engine="gpt-4o-mini"):
    scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=sr_id),
        open_ai_engine=open_ai_engine, is_test=True)
    scraper.record_articles(reset=True)
    scraper.make_preclassify_articles(block_size=block_size)


preclassify_articles(744, 17, "gpt-4o-mini")
preclassify_articles(450, 17, "gpt-4o-mini")
preclassify_articles(203, 17, "gpt-4o-mini")
preclassify_articles(102, 17, "gpt-4o-mini")
preclassify_articles(50, 17, "gpt-4o-mini")
preclassify_articles(22, 17, "gpt-4o-mini")


def scrape_full_articles(sr_id=17, block_size=1, open_ai_engine="gpt-4o-mini"):
    scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=sr_id),
        open_ai_engine=open_ai_engine, is_test=True)
    scraper.full_scrape_articles(all_articles=True, block_size=block_size)


scrape_full_articles(1, 20, "gpt-4o-2024-11-20")

scrape_full_articles(17, 20, "gpt-4o-mini")
scrape_full_articles(17, 6, "gpt-4o-mini")


#######

def counter_by_schema(sr_id=17):
    from django.db.models import Count
    all_schemas = QualifySchema.objects.filter(scraped_record__id=sr_id)
    total_articles = Article.objects.filter(scraped__id=sr_id).count()
    print(f"Total de artículos: {total_articles}")
    for schema in all_schemas:
        print(f"{schema} - ID: {schema.id}")
        qs = ArticleQualify.objects.filter(qualify_schema=schema)
        print(f"Artículos: {qs.count()}")
        counter = qs.values("change_value").annotate(Count("change_value"))
        for c in counter:
            print(f"{c['change_value']}: {c['change_value__count']}")
        print("-" * 20)


counter_by_schema(17)


def explore_schemas_by_article(sr_id=17):
    from source.models import Article, QualifySchema, ArticleQualify
    from django.db.models import Prefetch
    import csv

    # Get all schemas in one query
    all_schemas = list(QualifySchema.objects.filter(scraped_record__id=sr_id))

    # Fetch articles with their related qualifications in a single query
    articles = Article.objects.filter(scraped__id=sr_id).prefetch_related(
        Prefetch(
            'qualifications',
            queryset=ArticleQualify.objects.select_related('qualify_schema'),
            to_attr='all_qualifications'
        )
    )
    print(f"Total de artículos: {articles.count()}")
    schema_dict = {schema.id: str(schema) for schema in all_schemas}
    field_names = ["title", "url", "certainty_degree", "is_selected", "criteria"]
    sub_columns = ["selected", "certainty", "change", "criteria"]
    complete_columns = [f"{sub}_{str(schema)}" for schema in schema_dict.values()
                        for sub in sub_columns]

    final_data = []
    for article_obj in articles:
        try:
            title = article_obj.title.encode("latin-1")
        except Exception as e:
            print(f"Error: {e} with {article_obj.title}")
            title = article_obj.title.encode("utf-8")
        title = title.decode("latin-1")
        article_data = {
            "title": title,
            "url": article_obj.url,
            "certainty_degree": article_obj.certainty_degree,
            "is_selected": article_obj.is_selected,
            "criteria": article_obj.criteria,
            **{col: None for col in complete_columns}
        }

        for qualify in article_obj.all_qualifications:
            schema_str = schema_dict[qualify.qualify_schema_id]
            article_data[f"selected_{schema_str}"] = qualify.is_selected
            article_data[f"certainty_{schema_str}"] = qualify.certainty_degree
            article_data[f"change_{schema_str}"] = qualify.change_value
            article_data[f"criteria_{schema_str}"] = qualify.criteria

        final_data.append(article_data)

    file_path = f"fixture/articles_by_schema_{sr_id}.csv"

    with open(file_path, "w", newline="", encoding="latin-1") as file:

        writer = csv.DictWriter(
            file, fieldnames=field_names + complete_columns, delimiter="|")
        writer.writeheader()
        writer.writerows(final_data)

    print(f"Archivo guardado en: {file_path}")


explore_schemas_by_article(17)


def explore_diff_articles(change_value="minus", schema_id=5):
    articles = Article.objects.filter(
        qualifications__change_value=change_value,
        qualifications__qualify_schema__id=schema_id)
    for article in articles:
        print(article.title)
        print(article.url)


explore_diff_articles("minus", 5)
explore_diff_articles("plus", 5)


def update_all_articles_with_criteria():
    articles = Article.objects.filter(criteria__isnull=False)
    for article in articles:
        cert_degree = article.get_certainty_degree()
        article.certainty_degree = cert_degree
        article.save()


update_all_articles_with_criteria()
