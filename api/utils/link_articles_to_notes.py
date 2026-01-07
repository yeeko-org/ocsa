

def link_orphan_articles():
    from source.models import Article, Note
    orphan_articles = Article.objects.filter(
        note__isnull=True, is_selected=True)
    print(f"Found {orphan_articles.count()} orphan articles")
    for article in orphan_articles:
        linked_note = Note.objects.filter(
            title__contains=article.title,
            date=article.published_date,
            source=article.source
        )
        if linked_note.count() == 1:
            linked_note = linked_note.first()
            article.note = linked_note
            article.save()
            print(f"Linked Article {article.id} to Note {linked_note.id}")
        else:
            print(f"No matching Note found for Article {article.id} ({article})")

