from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'carga el archivo json de articulos y compara con las notas'

    def handle(self, *args, **options):

        from source.models import Note, Source
        from datetime import datetime

        # leer el archivo json

        import json
        with open("source/fixtures/articles_4o.json", "r") as file:
            data_4o = json.load(file)

        with open("source/fixtures/articles_4o_mini.json", "r") as file:
            data_4o_mini = json.load(file)

        from_date = data_4o["from_date"]
        to_date = data_4o["to_date"]
        print(f"Desde: {from_date} - Hasta: {to_date}")
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
        source_name = data_4o["source_name"]
        articles = data_4o["articles"]
        source = Source.objects.get(name=source_name)

        valid_articles = {
            article["url"]: article for article in articles
            if article["preclassification"] in ["valid", "maybe"]
        }
        articles_by_url = {article["url"]: article for article in articles}

        for note in notes:
            if not note.link:
                continue
            article = articles_by_url.get(note.link)
            if not article:
                print(f"Nota {note.link} sin articulo similar")
                print(f"Articulo: {note.title}")
                print("")
                continue
            # print(f"Nota {note.link} con articulo similar")
            print(f"Perfecto: {article['title']}")
            if certainty_degree := article.get("certainty_degree"):
                print(f"grado de criterios: {certainty_degree}")
            # print(f"grado de criterios: {article['certainty_degree']}")
            print("")
            _ = valid_articles.pop(note.link, None)

        if not valid_articles:
            return

        print("\n=== Artículos preclasificados válidos sin notas === \n")
        print(f"Total de Artículos: {len(valid_articles)}")
        for urls, article in valid_articles.items():
            print(f"Articulo: {article['title']}")
            print(f"preclasificado: {article['preclassification']}")
            print(f"url: {urls}")
            print("")
