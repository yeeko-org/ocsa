from typing import List, Optional
from ocsa_legacy.models import Nota
from source.models import Note, Source

from django.utils import timezone


class NotaToNote:
    source_list: List[Source] = []
    news_sources: List[str] = ['La Jornada', 'Reforma']
    errors: list = []

    def __init__(self):
        self.notas = Nota.objects.all()
        self.source_list = list(Source.objects.all())

        for nota in self.notas:
            try:
                self.migrate_nota(nota)
            except Exception as e:

                self.errors.append([nota, e])

    def migrate_nota(self, nota: Nota):
        source = self.get_source(nota.nombre_medio, nota.pagina_medio)
        print(f"Source: {source.name}")
        note = Note.objects.create(
            nota_id_ref=nota.pk,
            old_id=nota.id_nota,
            title=nota.titulo,
            author=nota.autor,
            source=source,
            link=nota.vinculo,
            date=nota.fecha or timezone.now().date(),
            capture_date=nota.fecha_captura
        )
        print(f"Created new note: {note}")

    def get_source(self, name: Optional[str], pagina_medio: Optional[str]):
        if not name:
            name = "unknown"

        for source in self.source_list:
            if source.name == name:
                return source

        source = Source.objects.create(
            name=name,
            main_url=pagina_medio,
            is_news=name in self.news_sources,
        )
        self.source_list.append(source)
        print(f"Created new source: {source}")

        return source
