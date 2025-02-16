from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'carga el archivo json de articulos y compara con las notas'

    def handle(self, *args, **options):

        from source.models import Note

        # leer el archivo json

        import json
        with open("source/fixtures/articles.json", "r") as file:
            data = json.load(file)

        from_date = data["from_date"]
        to_date = data["to_date"]
        source_id = data["source_id"]
        articles = data["articles"]

        valid_articles = {
            article["url"]: article for article in articles if article["preclasification"] in ["valid", "maybe"]
        }
        articles_by_url = {article["url"]: article for article in articles}

        notes = Note.objects.filter(
            date__range=[from_date, to_date], source__id=source_id)

        print(f"Notas: {notes.count()}")

        for note in notes:
            if not note.link:
                continue
            article = articles_by_url.get(note.link)
            if not article:
                continue
            print(f"Nota {note.link} con articulo similar")
            print(f"Articulo: {article['title']} - Nota: {note.title}")
            print(f"preclasificado: {article['preclasification']}")
            print(f"grado de criterios: {article['certainty_degree']}")
            print("")
            _ = valid_articles.pop(note.link, None)

        if not valid_articles:
            return

        print("Articulos preclasificados validos sin notas")
        for urls, article in valid_articles.items():
            print(f"Articulo: {article['title']}")
            print(f"preclasificado: {article['preclasification']}")
            print(f"url: {urls}")
            print("")
