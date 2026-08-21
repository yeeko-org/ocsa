"""Inventario de los artículos vetados por `is_political_opinion`.

Solo lee la base local; no llama a Gemini ni a la red. Sirve para
decidir el criterio de [[task-3]] leyendo casos concretos.

    python api/.claude/diagnostics/capped_political_opinion.py            # resumen
    python api/.claude/diagnostics/capped_political_opinion.py <id>       # un caso
"""
import os
import sys
from collections import Counter

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from source.models import Article  # noqa: E402


def capped_queryset(source=None):
    qs = Article.objects.filter(
        certainty_degree=98,
        criteria__is_political_opinion=True,
    ).select_related("source").order_by("published_date")
    if source:
        qs = qs.filter(source__name__icontains=source)
    return qs


def show_summary(source=None):
    qs = capped_queryset(source)
    print(f"Artículos capados a 98: {qs.count()}\n")

    print("Por fuente:")
    by_source = Counter(art.source.name for art in qs)
    for name, count in by_source.most_common():
        print(f"  {count:4}  {name}")
    print()

    sections = Counter()
    projects = Counter()
    rows = []
    for art in qs:
        crit = art.criteria or {}
        names = [p.get("name", "?") for p in crit.get("projects", [])]
        sections[art.section or "(sin sección)"] += 1
        for name in names:
            projects[name] += 1
        rows.append((art.id, art.published_date, art.section,
                     art.title, names))

    print("Por sección:")
    for section, count in sections.most_common():
        print(f"  {count:4}  {section}")

    print("\nProyectos detectados (nombre tal cual lo puso Gemini):")
    for name, count in projects.most_common(40):
        print(f"  {count:4}  {name}")

    print("\nCasos:")
    for art_id, date, section, title, names in rows:
        print(f"  [{art_id}] {date} · {section} · {title}")
        print(f"        proyectos: {', '.join(names) or '—'}")


def show_article(art_id: int):
    art = Article.objects.get(pk=art_id)
    crit = art.criteria or {}
    print(f"[{art.id}] {art.published_date} · {art.section}")
    print(f"Título: {art.title}")
    print(f"Autor: {art.author}")
    print(f"URL: {art.url}\n")
    print("criteria:")
    for key, value in crit.items():
        print(f"  {key}: {value}")
    print(f"\ndegree guardado: {art.certainty_degree}")
    print("\n--- párrafos ---")
    paragraphs = art.paragraphs or []
    for num, text in enumerate(paragraphs):
        if isinstance(text, dict):
            text = text.get("text", str(text))
        print(f"[{num}] {text}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg and arg.isdigit():
        show_article(int(arg))
    else:
        show_summary(arg)
