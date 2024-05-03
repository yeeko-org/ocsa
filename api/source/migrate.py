from typing import List, Optional
from ocsa_legacy.models import Nota
from source.models import Note, Source

from django.utils import timezone


class NotaToNote:
    source_list: List[Source] = []
    news_sources: List[str] = ['La Jornada', 'Reforma', 'Proceso']
    errors: list = []

    def __init__(self):
        self.show_creation = False
        Note.objects.all().delete()
        Source.objects.all().delete()
        self.notas = Nota.objects.all()
        self.source_list = list(Source.objects.all())

        for nota in self.notas:
            try:
                self.migrate_nota(nota)
            except Exception as e:

                self.errors.append([nota, e])

    def migrate_nota(self, nota: Nota):
        source = self.get_source(nota.nombre_medio)
        page, section = self.page_and_section(nota)
        # print(f"Source: {source.name}")
        note = Note.objects.create(
            nota_id_ref=nota.pk,
            old_id=nota.id_nota,
            title=nota.titulo,
            author=nota.autor,
            source=source,
            pages=page,
            section=section,
            link=nota.vinculo,
            date=nota.fecha or timezone.now().date(),
            capture_date=nota.fecha_captura
        )
        if self.show_creation:
            print(f"Created new note: {note}")

    def page_and_section(self, nota: Nota):
        import re
        pagina_medio = nota.pagina_medio
        if not pagina_medio:
            return None, None
        pagina_medio = pagina_medio.strip()
        if pagina_medio == "SD":
            return None, None
        pagina_medio = pagina_medio.replace("; SD", "").replace("SD;", "")
        pagina_medio = pagina_medio.strip()
        if not pagina_medio:
            return None, None
        if pagina_medio.isdigit():
            return pagina_medio, None
        # pagina_medio = pagina_medio.replace(",", ";").replace(":", ";")
        pagina_medio = re.sub(r'[,:\|]', ';', pagina_medio)
        pagina_medio = pagina_medio.replace("nea 12", "nea doce")

        def has_only_digits(string):
            string_without_spaces = re.sub(r'[; -]', '', string)
            return string_without_spaces.isdigit()

        def has_only_non_digits(string):
            return not any(char.isdigit() for char in string)

        if has_only_digits(pagina_medio):
            return pagina_medio, None
        try:
            section, page = pagina_medio.split(";")
            page = page.strip()
            section = section.strip()
            if has_only_digits(page) and has_only_non_digits(section):
                return page, section
            else:
                print(f"Error en split: {nota.pagina_medio} --> {pagina_medio}")
        except ValueError:
            pass

        first_number = re.search(r'\d', pagina_medio)
        if not first_number:
            section = pagina_medio.replace(";", "").strip()
            return None, section
        else:
            first_number = first_number.start()
            page = pagina_medio[first_number:].strip()
            section = pagina_medio[:first_number].strip()
            if has_only_digits(page) and has_only_non_digits(section):
                return page, section
            else:
                print(f"first_number: {first_number}, section: {section}, page: {page}")
                print(f"Error dividiendo: {nota.pagina_medio} --> {pagina_medio}")
        return None, None

    def get_source(self, name: Optional[str]):
        if not name:
            name = "unknown"

        for source in self.source_list:
            if source.name == name:
                return source

        source = Source.objects.create(
            name=name,
            is_news=name in self.news_sources,
        )
        self.source_list.append(source)
        if self.show_creation:
            print(f"Created new source: {source}")

        return source
