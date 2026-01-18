
def compare_versions(
        sr_id=50, ai_engine="gemini-3-flash-preview",
        prompt_version="v2", count: int=None):
    from source.scraper.jornada import JornadaManagerScraper
    from source.scraper.reforma import ReformaManagerScraper
    from source.models import ScrapedRecord, Article

    scraped_record = ScrapedRecord.objects.get(pk=sr_id)

    scraper_class = ReformaManagerScraper \
        if scraped_record.source.name == "Reforma" \
        else JornadaManagerScraper

    articles = Article.objects.filter(
        scraped=scraped_record, certainty_degree__gt=100
    ).order_by("-certainty_degree")
    if count:
        articles = articles[:count]

    scraper = scraper_class(
        "", "", recover_record=scraped_record,
        ai_engine=ai_engine, is_test=True)

    scraper.scrape_articles(update=True)
    scraper.articles_by_id = {article.id: article for article in articles}
    scraper.build_ai_criteria(prompt_version=prompt_version)


compare_versions(76, count=40)


def direct_second_criteria(
        sr_id=50, ai_engine="gemini-3-flash-preview",
        prompt_version="v2", count: int=None):
    from source.scraper.jornada import JornadaManagerScraper
    from source.scraper.reforma import ReformaManagerScraper
    from source.models import ScrapedRecord
    scraped_record = ScrapedRecord.objects.get(pk=sr_id)
    scraper_class = ReformaManagerScraper \
        if scraped_record.source.name == "Reforma" \
        else JornadaManagerScraper
    scraper = scraper_class(
        "", "", recover_record=ScrapedRecord.objects.get(pk=sr_id),
        ai_engine=ai_engine, is_test=True)
    pending_articles = scraper.get_articles_objects(is_second=True)
    if count:
        pending_articles = pending_articles[:count]
    scraper.build_second_criteria(
        prompt_version=prompt_version, articles=pending_articles)


direct_second_criteria(83, count=8)


def second_year(year=2024, source_id=1):
    from source.models import ScrapedRecord
    scraped_records = ScrapedRecord.objects.filter(
        source__id=source_id,
        from_date__year=year,
        to_date__year=year,
    )
    for sr in scraped_records:
        print(f"Rewriting ScrapedRecord ID: {sr.id}; "
              f"Date Range: {sr.from_date} to {sr.to_date}")
        direct_second_criteria(sr.id)



def rewrite_first_criteria(
        sr_id=50, ai_engine="gemini-3-flash-preview",
        prompt_version="v2", count: int=None):
    from source.scraper.jornada import JornadaManagerScraper
    from source.scraper.reforma import ReformaManagerScraper
    from source.models import ScrapedRecord, Article
    scraped_record = ScrapedRecord.objects.get(pk=sr_id)
    scraper_class = ReformaManagerScraper \
        if scraped_record.source.name == "Reforma" \
        else JornadaManagerScraper
    articles = Article.objects\
        .filter(
        scraped=scraped_record, certainty_degree__gt=100,
        is_selected__isnull=True)\
        .order_by("-certainty_degree")
    if count:
        articles = articles[:count]
    scraper = scraper_class(
        "", "", recover_record=scraped_record, ai_engine=ai_engine)
    scraper.scrape_articles(update=True)
    scraper.articles_by_id = {article.id: article for article in articles}
    scraper.build_ai_criteria(prompt_version=prompt_version)


rewrite_first_criteria(57)

def rewrite_year(year=2024, source_id=2):
    from source.models import ScrapedRecord
    scraped_records = ScrapedRecord.objects.filter(
        source__id=source_id,
        from_date__year=year,
        to_date__year=year,
    ).exclude(id__in=[53, 36, 57, 30])
    for sr in scraped_records:
        print(f"Rewriting ScrapedRecord ID: {sr.id}; "
              f"Date Range: {sr.from_date} to {sr.to_date}")
        rewrite_first_criteria(sr.id)


rewrite_year(2024, 1)



def get_again_old_articles(
        sr_id=78, ai_engine="gemini-3-flash-preview",
        prompt_version="v2", limit=5):
    # from source.scraper.reforma import ReformaManagerScraper
    from source.scraper.jornada import JornadaManagerScraper
    from source.models import ScrapedRecord, Article, Note
    scraped_record = ScrapedRecord.objects.get(pk=sr_id)
    scraper_class = JornadaManagerScraper
    pending_notes = Note.objects.filter(
        date__lte="2023-12-31",
        articles__isnull=True,
        source=scraped_record.source,
        link__isnull=False
    ).distinct()
    print(f"Total de notas pendientes: {pending_notes.count()}")
    for note in pending_notes[:limit]:
        has_same_url = Article.objects.filter(url=note.link).exists()
        if has_same_url:
            print(f"Nota ya tiene artículo asociado: {note.link}")
            print(f"title: {note.title}")
            continue
        uid = note.link.replace("https://www.jornada.com.mx/", "")
        Article.objects.create(
            scraped=scraped_record,
            uid=uid,
            source=scraped_record.source,
            url=note.link,
            title="",
            note=note,
            is_selected=True,
            certainty_degree=101,
            published_date=note.date
        )
    scraper = scraper_class(
        "", "", recover_record=scraped_record, ai_engine=ai_engine)
    scraper.scrape_articles(update=True)
    articles_objects = scraper.get_articles_objects()
    for article in articles_objects:
        if note := article.note:
            note.subtitle = article.subtitle
            note.save()
    first_selected_articles = list(Article.objects.filter(
        scraped=scraped_record,
        paragraphs__isnull=False,
        second_criteria__isnull=True
    ))
    print(f"Total de artículos para segunda evaluación: "
          f"{len(scraper.first_selected_articles)}")
    scraper.build_second_criteria(
        prompt_version=prompt_version, articles=first_selected_articles)


get_again_old_articles(86, limit=522)



def examples():
    from source.scraper.jornada import JornadaManagerScraper
    from source.scraper.reforma import ReformaManagerScraper
    from source.models import (
        ScrapedRecord, Article, QualifySchema, ArticleQualify, Note)

    manager_scraper = JornadaManagerScraper(
        "2023/04/01", "2023/04/03", ai_engine="gemini-3-flash-preview")

    manager_reforma = ReformaManagerScraper(
        "2024/04/01", "2023/04/03", ai_engine="gemini-3-flash-preview")

    # print(manager_scraper.scraped_record)
    print(manager_reforma.scraped_record.id)
    manager_scraper.scrape_sections()
    manager_reforma.scrape_sections()

    manager_scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=42),
        ai_engine="gemini-3-flash-preview")

    manager_reforma = ReformaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=83),
        ai_engine="gemini-3-flash-preview")

    manager_scraper.record_articles(reset=True)
    manager_reforma.record_articles(reset=True)

    manager_scraper.scrape_articles(update=True)
    manager_reforma.scrape_articles(update=True)

    manager_reforma.scraped_record.articles.update(
        html_content=None, title=None, subtitle=None, author=None,
        content=None, images=None)
    manager_reforma.scrape_articles(update=True)

    manager_scraper.build_ai_criteria(prompt_version="v1")

    manager_reforma.build_ai_criteria(prompt_version="v2")

    # QualifySchema.objects.all().delete()
    Article.objects.filter(scraped__id=45).count()

    ########

    # python manage.py articles_json "2022-03-01" "2022-03-28" 4
    # python manage.py compare_notes --settings=core.settings_prod
    ########


def test_paragraphs():
    from source.scraper.jornada import JornadaArticleScraper
    from source.models import Article
    article_obj = Article.objects.get(id=32187)
    scraper = JornadaArticleScraper(article_obj, update=True)
    self = scraper


def test_reforma_subtitle():
    from source.scraper.reforma import ReformaArticleScraper
    from source.models import Article
    article_obj = Article.objects.get(id=34637)
    scraper = ReformaArticleScraper(article_obj, update=True)
    scraper.get_reduced_content_text()
    self = scraper




def scrape_full_articles(
        sr_id=17, ai_engine="gemini-3-flash-preview",
        prompt_version="v2"):
    from source.scraper.jornada import JornadaManagerScraper
    from source.scraper.reforma import ReformaManagerScraper
    from source.models import ScrapedRecord

    scraper = JornadaManagerScraper(
        "", "", recover_record=ScrapedRecord.objects.get(pk=sr_id),
        ai_engine=ai_engine, is_test=True)

    # if ai_engine == "deepseek-chat":
    #     scraper.use_deepseek = True
    scraper.scrape_articles()
    scraper.articles_by_id = {}
    scraper.build_ai_criteria(prompt_version=prompt_version)


scrape_full_articles(42, prompt_version="v1")
scrape_full_articles(42, prompt_version="v2")

# scrape_full_articles(22, 6, "gemini-3-flash-preview", "v2")
# scrape_full_articles(22, 6, "gemini-3-flash-preview", "v1")
# scrape_full_articles(22, 6, "deepseek-chat", "v1")

# scrape_full_articles(1, 20, "gpt-4o-2024-11-20")
# scrape_full_articles(17, 20, "gemini-3-flash-preview")


#######



def counter_by_schema(sr_id=17):
    from django.db.models import Count
    from source.models import Article, QualifySchema, ArticleQualify
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
    import json

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
    field_names = ["title", "url", "has_note",
                   "certainty_degree", "is_selected", "criteria"]
    sub_columns = ["selected", "certainty", "criteria", "change", "icon"]
    complete_columns = [f"{sub}_{str(schema)}" for schema in schema_dict.values()
                        for sub in sub_columns]

    all_url_notes = Note.objects.filter(
        source__name="La Jornada").values_list("link", flat=True)
    other_url_notes = [
        "https://www.jornada.com.mx/2022/08/01/estados/024n2est",
        "https://www.jornada.com.mx/2022/09/01/politica/012n3pol",
        "https://www.jornada.com.mx/2022/09/04/estados/020n1est",
        "https://www.jornada.com.mx/2022/09/05/opinion/021o1eco",
        "https://www.jornada.com.mx/2022/09/05/politica/011n2pol",
        "https://www.jornada.com.mx/2022/09/06/estados/028n1est",
        "https://www.jornada.com.mx/2022/09/06/politica/012n2pol",
        "https://www.jornada.com.mx/2022/09/07/estados/026n1est",
        "https://www.jornada.com.mx/2022/09/08/estados/027n1est",
        "https://www.jornada.com.mx/2022/09/12/estados/025n1est",
        "https://www.jornada.com.mx/2022/09/13/politica/011n1pol",
        "https://www.jornada.com.mx/2022/09/14/politica/012n2pol",
        "https://www.jornada.com.mx/2022/09/17/cultura/a03n1cul",
        "https://www.jornada.com.mx/2022/09/18/estados/025n1est",
        "https://www.jornada.com.mx/2022/09/18/estados/025n2est",
        "https://www.jornada.com.mx/2022/09/19/capital/036n1cap",
        "https://www.jornada.com.mx/2022/09/21/estados/028n1est",
        "https://www.jornada.com.mx/2022/09/21/capital/032n2cap",
        "https://www.jornada.com.mx/2022/09/24/capital/028n1cap",
        "https://www.jornada.com.mx/2022/09/24/estados/025n1est",
        "https://www.jornada.com.mx/2022/09/25/estados/022n1est",
        "https://www.jornada.com.mx/2022/09/26/estados/030n1est",
        "https://www.jornada.com.mx/2022/09/26/estados/030n1est",
        "https://www.jornada.com.mx/2022/09/25/estados/022n1est",
        "https://www.jornada.com.mx/2022/09/26/estados/029n1est",
        "https://www.jornada.com.mx/2022/09/21/estados/028n1est",
        "https://www.jornada.com.mx/2022/09/18/estados/025n1est",
        "https://www.jornada.com.mx/2022/09/06/politica/012n2pol"
    ]
    all_url_notes = list(all_url_notes) + other_url_notes

    icons = {
        "minus": 1,  # "❌",
        "plus": 4,  # "✅",
        "selected": 3,  # "➡️",
        "not_selected": 2  # "🟰",
    }
    final_data = []
    for article_obj in articles:
        if article_obj.url == 'https://www.jornada.com.mx/2022/07/25/estados/031n1est':
            continue
        try:
            title = article_obj.title.encode("latin-1")
            criteria = json.dumps(article_obj.criteria).encode("latin-1")
        except Exception as e:
            print(f"Error 1: {e} with {article_obj.title}")
            title = article_obj.title.encode("utf-8")
            criteria = json.dumps({}).encode("utf-8")
        title = title.decode("latin-1")
        criteria = criteria.decode("latin-1")
        criteria = json.loads(criteria)

        article_data = {
            "title": title,
            "url": article_obj.url,
            "has_note": 1 if article_obj.url in all_url_notes else 0,
            "is_selected": 1 if article_obj.is_selected else 0,
            "certainty_degree": article_obj.certainty_degree,
            "criteria": criteria,

            **{col: None for col in complete_columns}
        }

        for qualify in article_obj.all_qualifications:
            schema_str = schema_dict[qualify.qualify_schema_id]
            is_selected = 1 if qualify.is_selected else 0
            article_data[f"selected_{schema_str}"] = is_selected
            article_data[f"certainty_{schema_str}"] = qualify.certainty_degree
            try:
                curr_criteria = json.dumps(qualify.criteria).encode("latin-1")
            except Exception as e:
                print(f"Error 2: {e} with {qualify.criteria}")
                curr_criteria = json.dumps({}).encode("utf-8")
            article_data[f"criteria_{schema_str}"] = json.loads(curr_criteria)
            change_value = qualify.change_value
            article_data[f"change_{schema_str}"] = change_value
            article_data[f"icon_{schema_str}"] = icons.get(change_value, 2.1)

        final_data.append(article_data)

    print("len(final_data):", len(final_data))
    # mini_data = final_data[:1000]
    # for article in mini_data:
    #     print(article)

    file_path = f"fixture/articles_by_schema_{sr_id}.csv"
    # for x in range(0, len(final_data), 2):
    #     mini_data = final_data[x:x+2]
    with open(file_path, "w", newline="", encoding="latin-1") as file:
        writer = csv.DictWriter(
            file, fieldnames=field_names + complete_columns, delimiter="|")
        writer.writeheader()
        # try:
        #     writer.writerows(mini_data)
        # except Exception as e:
        #     print(f"Error 3: {e} with: \n\n\n {mini_data}")
        writer.writerows(final_data)

    print(f"Archivo guardado en: {file_path}")


explore_schemas_by_article(22)


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
    from source.models import Article
    articles = Article.objects.filter(criteria__isnull=False)
    for article in articles:
        cert_degree = article.get_certainty_degree_v2()
        article.certainty_degree = cert_degree
        article.save()


update_all_articles_with_criteria()


def delete_prev_articles():
    from source.models import Article
    print(Article.objects.filter(criteria__isnull=True).count())
    print(Article.objects.filter(criteria__isnull=False).count())
    Article.objects.filter(criteria__icontains='"{').delete()
    Article.objects.exclude(criteria__icontains='projects').delete()
    Article.objects.filter(scraped__id=18).delete()
