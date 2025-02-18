# Ejecucion de pruebas de scraping por pasos completos, y sus formas de ver la informacion.

from pprint import pprint
from source.scraper.jornada import JornadaManagerScraper
from source.models import (
    ScrapedRecord, Article, QualifySchema, ArticleQualify)

manager_scraper = JornadaManagerScraper(
    "2022/03/01", "2022/03/28", open_ai_engine="gpt-4o-mini")

# print(manager_scraper.scraped_record)
manager_scraper.scrape_sections()

manager_scraper = JornadaManagerScraper(
    "", "", recover_record=ScrapedRecord.objects.get(pk=17),
    open_ai_engine="gpt-4o-mini")

manager_scraper = JornadaManagerScraper(
    "", "", recover_record=ScrapedRecord.objects.last(),
    open_ai_engine="gpt-4o-mini")

manager_scraper.record_articles(reset=True)

manager_scraper.full_scrape_articles(all_articles=True, block_size=1)

QualifySchema.objects.all().delete()
Article.objects.filter(scraped__id=17).count()

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


def full_scrape_articles(sr_id=17, block_size=1, open_ai_engine="gpt-4o-mini"):
    scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=sr_id),
        open_ai_engine=open_ai_engine, is_test=True)
    scraper.full_scrape_articles(all_articles=True, block_size=block_size)


full_scrape_articles(17, 20, "gpt-4o-mini")
full_scrape_articles(17, 5, "gpt-4o-mini")


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


def explore_diff_articles(change_value="minus", schema_id=5):
    articles = Article.objects.filter(
        qualifications__change_value=change_value,
        qualifications__qualify_schema__id=schema_id)
    for article in articles:
        print(article.title)
        print(article.url)


explore_diff_articles("minus", 5)
explore_diff_articles("plus", 5)


def default_st_to_projects():
    from project.models import Project
    Project.objects.filter(status_validation__isnull=True).update(
        status_validation_id='original')

