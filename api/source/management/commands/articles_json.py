from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Geners un archivo json de los articulos'
    articles = None

    def add_arguments(self, parser):

        parser.add_argument('from_date', type=str)
        parser.add_argument('to_date', type=str)
        parser.add_argument('source_id', type=int)

    def handle(self, *args, **options):
        from source.models import Article, Source

        from_date = options['from_date']
        to_date = options['to_date']
        source_id = options['source_id']

        # guarda un archivo en source/fixtures/articles.json
        source = Source.objects.get(id=source_id)
        self.articles = Article.objects.filter(
            published_date__range=[from_date, to_date], source__id=source_id)

        data = {
            "from_date": from_date,
            "to_date": to_date,
            "source_id": source_id,
            "source_name": source.name,
            "articles": [
                {
                    "title": article.title,
                    "url": article.url,
                    "preclassification": article.preclassification,
                    "is_selected": article.is_selected,
                    "criteria": article.criteria,
                    # "certainty_degree": article.get_certainty_degree(),
                }
                for article in self.articles
            ]
        }

        import json
        with open("source/fixtures/articles.json", "w") as file:
            json.dump(data, file, indent=4)
        print("Archivo generado")
        print(f"Articulos: {len(data['articles'])}")
        print(f"Archivo guardado en source/fixtures/articles.json")