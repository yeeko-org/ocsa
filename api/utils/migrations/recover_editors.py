

# rescatar editores no registrados, pero sí guardados como revisores

def run():
    from source.models import Note
    missing_editors = Note.objects\
        .filter(editors__isnull=True, reviewers__isnull=False)\
        .distinct()
    print(f"Found {missing_editors.count()} "
          f"notes with missing editors but with reviewers.")
    for note in missing_editors:
        reviewers_count = note.reviewers.count()
        if reviewers_count == 1:
            reviewer = note.reviewers.first()
            if reviewer:
                note.editors.add(reviewer)
        else:
            for reviewer in note.reviewers.all():
                if reviewer.id == 21:
                    note.editors.add(reviewer)
                    break




def explore_orphan_editors():
    from source.models import Note
    orphan_editors = Note.objects\
        .filter(editors__isnull=True, reviewers__isnull=True)\
        .order_by("?")\
        .distinct()
    print(f"Found {orphan_editors.count()} "
          f"notes with missing editors and missing reviewers.")
    real_orphan_notes = orphan_editors.filter(editor__isnull=True)
    print(f"Found {real_orphan_notes.count()} "
          f"notes with missing editors and missing reviewers, "
          f"and no editor assigned.")
    for note in orphan_editors[:40]:
        print(f"Note ID: {note.id}; nota_id_ref: {note.nota_id_ref},"
              f" Title: {note.title}")


# explore_orphan_editors()


