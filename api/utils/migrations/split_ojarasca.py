from source.models import Source, Note
from django.db.models import Count


def methods():
    ojarasca_source = Source.objects.get(name__icontains="Ojarasca")

    jornada_source = Source.objects.get(name="La Jornada")


    by_link = Note.objects.filter(link__icontains="ojarasca")
    by_section = Note.objects.filter(section__icontains="ojarasca")
    by_note_file = Note.objects.filter(files__file__icontains="ojarasca")


    by_link.update(source=ojarasca_source)
    by_section.update(source=ojarasca_source)
    by_note_file.update(source=ojarasca_source)


    notes_jornada_no_link = Note.objects\
        .filter(source=jornada_source, section__isnull=True)\
        .exclude(link__icontains="jornada")\
        .exclude(files__file__icontains="jornada")\
        .distinct()


    notes_jornada = Note.objects.filter(source=jornada_source)


    notes_jornada.count()
    notes_jornada_no_link.count()

    group_by_section = notes_jornada.values('section').annotate(count=Count('id')).order_by('-count')
    for section in group_by_section:
        print(f"{section['section']}: {section['count']}")


    ecologica = Note.objects.filter(
        source=jornada_source, title__icontains="Del Campo", link__isnull=True)


    # for note in ecologica:
    for note in notes_jornada_no_link:
        print("-" * 40)
        print(note.title)
        if note.link:
            print(note.link)
        for file in note.files.all():
            print(file.file.url)
        print("autor:", note.author)


    por_checar = Note.objects.filter(source=jornada_source, title__icontains="revisar sección")

    # revertir por_checar:
    for note in por_checar:
        note.title = note.title.replace(" (revisar sección)", "")
        note.section = 'Ojarasca'
        note.source = ojarasca_source
        note.save()

