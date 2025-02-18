from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'carga el archivo json de articulos y compara con las notas'

    def handle(self, *args, **options):

        from source.models import Note, Source, Article
        from datetime import datetime

        # leer el archivo json

        import json
        with open("source/fixtures/articles.json", "r") as file:
            data = json.load(file)

        from_date = data["from_date"]
        to_date = data["to_date"]
        print(f"Desde: {from_date} - Hasta: {to_date}")
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
        source_id = data["source_id"]
        source_name = data["source_name"]
        articles = data["articles"]
        source = Source.objects.get(name=source_name)

        valid_articles = {
            article["url"]: article for article in articles
            # if article["preclassification"] in ["valid", "maybe", "unknown"]
            if article["is_selected"]
        }
        articles_by_url = {article["url"]: article for article in articles}

        notes = Note.objects.filter(
            date__range=[from_date, to_date], source=source)
        # date__gte = from_date, date__lte = to_date, source__id = source_id)

        print(f"\nNotas guardadas: {notes.count()}\n")

        for note in notes:
            if not note.link:
                continue
            article = articles_by_url.get(note.link)
            if note.link not in valid_articles:
                print(f"!! Nota {note.link} sin articulo similar")
                print(f"Articulo: {note.title}")
                if article:
                    print("Articulo encontrado\n")
                else:
                    print("-----")
                continue
            # print(f"Nota {note.link} con articulo similar")
            print(f"Perfecto: {article['title']} ({article['preclassification']})")
            if certainty_degree := article.get("certainty_degree"):
                print(f"grado de criterios: {certainty_degree}")
            # print(f"grado de criterios: {article['certainty_degree']}")
            # print("")
            _ = valid_articles.pop(note.link, None)

        if not valid_articles:
            return

        print("\n=== Artículos preclasificados válidos sin notas === \n")
        print(f"Total de Artículos: {len(valid_articles)}")
        for urls, article in valid_articles.items():
            print(f"{article['preclassification']}: {article['title']}")
            print(f"url: {urls}")
