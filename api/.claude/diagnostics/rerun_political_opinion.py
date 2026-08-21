"""Corrida A/B del §4 del prompt v3 sobre una muestra estratificada.

Clasifica con `is_test=True`, así que escribe en `ArticleQualify` y NO
toca `Article.criteria` ni `certainty_degree`. Golpea Gemini: ~59
llamadas por corrida completa. Es reanudable —salta lo ya calificado
con el mismo esquema—, así que re-ejecutarla no vuelve a cobrar.

    python api/.claude/diagnostics/rerun_political_opinion.py run
    python api/.claude/diagnostics/rerun_political_opinion.py report

Ojo con las etiquetas de `ArticleQualify.CHANGE_OPTIONS`: están escritas
asumiendo que lo guardado es la verdad, así que `plus` («erróneamente
incluido») aquí significa que el criterio nuevo recupera un artículo que
el viejo vetaba, que es justo lo que buscamos medir.
"""
import os
import sys
from collections import Counter

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from source.models import (  # noqa: E402
    Article, ArticleQualify, QualifySchema, ScrapedRecord, Source)

AI_ENGINE = os.getenv("ENGINE", "gemini-3-flash-preview")
PROMPT_VERSION = "v3"
# El archivo del prompt se edita in situ, así que la versión no distingue
# rondas: cada iteración de redacción usa su propio lote marcador.
ROUND = int(os.getenv("ROUND", "2"))
MARKER_DATES = ("1900-02-01", f"1900-02-{ROUND + 1:02d}")
FAMOUS = ["Tren Maya", "Dos Bocas", "Felipe Ángeles", "AIFA",
          "Interoceánico", "Texcoco"]
INFORMATIVE = ["Política", "Estados", "Capital", "Economía",
               "Sociedad y Justicia"]


def capped(source_name=None, exclude=False):
    qs = Article.objects.filter(
        certainty_degree=98, criteria__is_political_opinion=True)
    if source_name:
        lookup = {"source__name": source_name}
        qs = qs.exclude(**lookup) if exclude else qs.filter(**lookup)
    return qs.order_by("id")


def is_famous(article):
    names = " ".join(
        p.get("name", "") for p in (article.criteria or {}).get("projects", []))
    return any(word in names for word in FAMOUS)


def spread(items, size):
    """Muestreo determinista y disperso: evita sesgar por fecha o lote."""
    items = list(items)
    if len(items) <= size:
        return items
    step = len(items) / size
    return [items[int(i * step)] for i in range(size)]


def build_sample():
    jornada = capped("La Jornada")
    others = list(capped("La Jornada", exclude=True))
    groups = {
        "A_jornada_informativa": spread(
            jornada.filter(section__in=INFORMATIVE), 12),
        "B_jornada_opinion": spread(jornada.filter(section="Opinión"), 12),
        "C_otras_famoso": spread(
            [a for a in others if is_famous(a)], 12),
        "D_otras_no_famoso": spread(
            [a for a in others if not is_famous(a)], 8),
        "E_control_pasan": spread(
            Article.objects.filter(
                certainty_degree__gt=100,
                criteria__isnull=False).order_by("id"), 15),
    }
    return groups


def get_schema_record():
    source = Source.objects.first()
    record, _ = ScrapedRecord.objects.get_or_create(
        from_date=MARKER_DATES[0], to_date=MARKER_DATES[1], source=source)
    return record


def run():
    from source.criteria.first import FirstCriteriaManager

    groups = build_sample()
    record = get_schema_record()
    schema, _ = QualifySchema.objects.get_or_create(
        scraped_record=record, ia_model=AI_ENGINE,
        prompt_version=PROMPT_VERSION, batch_size=1)

    done = set(ArticleQualify.objects
               .filter(qualify_schema=schema)
               .values_list("article_id", flat=True))
    pending = []
    for name, articles in groups.items():
        fresh = [a for a in articles if a.id not in done]
        print(f"{name}: {len(articles)} en muestra, {len(fresh)} pendientes")
        pending.extend(fresh)

    if not pending:
        print("\nNada pendiente. Corre `report`.")
        return

    print(f"\nClasificando {len(pending)} artículos con {AI_ENGINE}...")
    manager = FirstCriteriaManager(
        recover_record=record, ai_engine=AI_ENGINE, is_test=True,
        prompt_version=PROMPT_VERSION)
    # El default de la clase es 2 s, que da ~0.6 s de margen por artículo
    # sobre el ritmo real: un solo stall de la API expira el caché y tumba
    # el resto del lote.
    manager.seconds_cache = 30
    manager.build_criteria(articles=pending)
    print("Listo. Corre `report`.")


def get_schema(round_number, engine=None):
    return QualifySchema.objects.filter(
        ia_model=engine or AI_ENGINE, prompt_version=PROMPT_VERSION,
        scraped_record__from_date="1900-02-01",
        scraped_record__to_date=f"1900-02-{round_number + 1:02d}").first()


def report():
    groups = build_sample()
    schema = get_schema(ROUND)
    if not schema:
        print("No hay corrida todavía.")
        return

    quals = {q.article_id: q for q in ArticleQualify.objects
             .filter(qualify_schema=schema).select_related("article")}
    prev_round = int(os.getenv("PREV_ROUND", str(ROUND - 1)))
    prev_engine = os.getenv("PREV_ENGINE", AI_ENGINE)
    prev_schema = get_schema(prev_round, prev_engine) if prev_round else None
    prev = {}
    if prev_schema:
        prev = {q.article_id: q.certainty_degree for q in
                ArticleQualify.objects.filter(qualify_schema=prev_schema)}

    for name, articles in groups.items():
        print(f"\n=== {name} ===")
        counts = Counter()
        for art in articles:
            qual = quals.get(art.id)
            if not qual:
                counts["sin_correr"] += 1
                continue
            was = bool((art.criteria or {}).get("is_political_opinion"))
            now = bool((qual.criteria or {}).get("is_political_opinion"))
            counts[qual.change_value] += 1
            flag = "→" if was != now else " "
            before = prev.get(art.id)
            middle = f"{before:>3} → " if before is not None else ""
            print(f"  [{art.id}] {art.certainty_degree:>3} → {middle}"
                  f"{qual.certainty_degree:>3}  {flag} opinion "
                  f"{was}→{now}  {qual.change_value}")
            print(f"        {art.section} · {art.title}")
        print(f"  {dict(counts)}")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "report"
    if action == "run":
        run()
    elif action == "sample":
        for group, arts in build_sample().items():
            print(f"\n=== {group} ({len(arts)}) ===")
            for art in arts:
                print(f"  [{art.id}] {art.source.name} · {art.section} · "
                      f"{art.title}")
    else:
        report()