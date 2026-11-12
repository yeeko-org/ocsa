"""Exporta la muestra de artículos a JSONL para el experimento jev-qwen.

Solo lectura contra la BD. No toca Gemini ni escribe nada en OCSA.

    python api/.claude/diagnostics/export_jev_sample_articles.py

Estratos (composición decidida por Ricardo el 2026-09-18):
  alto       certainty_degree > 100
  borde      72 <= certainty_degree <= 99 (pocos features, o vetados
             con tope 97/98)
  aleatorio  cualquier artículo con texto, excluyendo lo ya tomado

El tamaño no está fijado: cada estrato toma `MIN_PER_CELL` (16) por
celda y el total es lo que salga de ahí. La cuota fija dejaba fuera los
casos raros, y Ricardo prefiere una muestra más grande y desigual con
todos los casos representados. Si una celda tiene menos de ese piso se
toma entera y se reporta.

La celda es (fuente, año de publicación); en el borde con
`BORDE_MODE=balanceado` la celda es el valor de `certainty_degree`, para
que los vetados 97/98 no queden sepultados bajo el 95. Ahí la fuente
deja de ser celda, así que además rige un piso por fuente: la que tenga
menos de `MIN_PER_CELL` notas en el pool entra entera.

El muestreo es determinista: dentro de cada celda se elige con
`spread()` —el mismo muestreo disperso ya aceptado en
`rerun_political_opinion.py`—, así que dos corridas dan el mismo archivo.

Con `MIN_PER_CELL=0` vuelve el reparto anterior por cuota fija
(`STRATA`), proporcional al tamaño de cada celda.
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db.models.functions import Length  # noqa: E402
from source.models import Article  # noqa: E402
from source.criteria.first import FirstCriteriaManager  # noqa: E402

SEED = 20260918
OUT_DIR = os.path.expanduser("~/dev/mini/jev-qwen/data/raw")
OUT_FILE = os.path.join(OUT_DIR, "articles_sample.jsonl")
MIN_CHARS, MAX_CHARS = 500, 12000
# Solo se usan con MIN_PER_CELL=0, el modo de cuota fija anterior.
STRATA = [("alto", 150), ("borde", 75), ("aleatorio", 75)]
# `proporcional` (default) respeta la forma del pool del borde;
# `balanceado` trata cada valor de certainty_degree como una celda.
BORDE_MODE = os.getenv("BORDE_MODE", "proporcional")
MIN_PER_CELL = int(os.getenv("MIN_PER_CELL", "16"))


def base_queryset():
    """Universo común: con párrafos y con cuerpo de 500 a 12 000 chars."""
    return Article.objects.annotate(clen=Length("content")).filter(
        paragraphs__isnull=False, clen__gte=MIN_CHARS, clen__lte=MAX_CHARS
    ).exclude(paragraphs=[]).select_related("source", "discarded_reason")


def spread(items, size):
    """Muestreo determinista y disperso: evita sesgar por fecha o lote."""
    items = list(items)
    if size <= 0:
        return []
    if len(items) <= size:
        return items
    step = len(items) / size
    return [items[int(i * step)] for i in range(size)]


def cell_key(article):
    """Celda de muestreo: fuente y año de publicación."""
    year = (article.published_date.year
            if article.published_date else None)
    return (article.source.name, year)


def degree_key(article):
    return article.certainty_degree


def floor_by_cell(articles, minimum, key=cell_key):
    """Toma hasta `minimum` por celda; el total es lo que resulte.

    Devuelve también las celdas que no alcanzan el piso, porque una
    celda corta es un dato del pool que hay que reportar, no un error.
    """
    cells = defaultdict(list)
    for art in articles:
        cells[key(art)].append(art)
    picked, short = [], []
    for name in sorted(cells, key=repr):
        arts = sorted(cells[name], key=lambda a: a.id)
        if len(arts) < minimum:
            short.append((name, len(arts)))
        picked.extend(spread(arts, min(minimum, len(arts))))
    return sorted(picked, key=lambda a: a.id), short


def small_sources(articles, minimum):
    """Fuentes con menos de `minimum` notas en el pool, enteras.

    En el borde la celda es el grado, no la fuente, así que una fuente
    marginal puede no ganar ni un lugar: Proceso tiene 6 notas en la
    banda 72-99 y quedaba en cero. Ricardo decidió el 2026-09-18 que
    esas notas entren completas.
    """
    cells = defaultdict(list)
    for art in articles:
        cells[art.source.name].append(art)
    picked = []
    for name in sorted(cells):
        if len(cells[name]) < minimum:
            picked.extend(cells[name])
    return picked


def spread_by_cell(articles, size):
    """Reparte `size` entre las celdas (fuente, año) y aplica `spread`.

    Reparto proporcional por resto mayor; el sobrante se asigna a las
    celdas con mayor resto y, a igualdad de resto, en un orden barajado
    con `SEED` para no favorecer siempre a la misma fuente.
    """
    articles = list(articles)
    if len(articles) <= size:
        return articles

    cells = defaultdict(list)
    for art in articles:
        cells[cell_key(art)].append(art)
    for arts in cells.values():
        arts.sort(key=lambda a: a.id)

    total = len(articles)
    keys = sorted(cells, key=lambda k: (k[0], -1 if k[1] is None else k[1]))
    quotas, remainders = {}, []
    for key in keys:
        exact = len(cells[key]) * size / total
        quotas[key] = int(exact)
        remainders.append((exact - int(exact), key))

    rng = random.Random(SEED)
    rng.shuffle(remainders)
    remainders.sort(key=lambda pair: pair[0], reverse=True)
    left = size - sum(quotas.values())
    for _, key in remainders[:left]:
        quotas[key] += 1

    picked = []
    for key in keys:
        picked.extend(spread(cells[key], quotas[key]))
    # El reparto por celda puede quedar corto si alguna celda es menor
    # que su cuota; se completa con el resto, disperso sobre el global.
    if len(picked) < size:
        chosen = {a.id for a in picked}
        rest = [a for a in sorted(articles, key=lambda a: a.id)
                if a.id not in chosen]
        picked.extend(spread(rest, size - len(picked)))
    return sorted(picked, key=lambda a: a.id)


def balanced_by_degree(articles, size):
    """Cuota pareja por valor de `certainty_degree` dentro del borde.

    El pool del borde está dominado por el 95 (proyecto sin features);
    con reparto proporcional los vetados (97/98) casi no aparecen. Este
    modo reparte la cuota en rondas entre los valores presentes, así que
    cada valor entra con todo lo que tenga hasta agotar la muestra.
    """
    groups = defaultdict(list)
    for art in articles:
        groups[art.certainty_degree].append(art)
    quotas = {degree: 0 for degree in groups}
    left = min(size, sum(len(g) for g in groups.values()))
    while left:
        openers = [d for d in sorted(groups) if quotas[d] < len(groups[d])]
        share = max(1, left // len(openers))
        for degree in openers:
            if not left:
                break
            add = min(share, len(groups[degree]) - quotas[degree], left)
            quotas[degree] += add
            left -= add
    picked = []
    for degree in sorted(groups):
        picked.extend(spread_by_cell(groups[degree], quotas[degree]))
    return sorted(picked, key=lambda a: a.id)


def build_sample():
    base = base_queryset()
    pools = {
        "alto": base.filter(certainty_degree__gt=100),
        "borde": base.filter(
            certainty_degree__gte=72, certainty_degree__lte=99),
    }
    sample, taken, short = [], set(), []
    for name, size in STRATA:
        if name == "aleatorio":
            pool = base.exclude(id__in=sorted(taken))
        else:
            pool = pools[name]
        balanced = name == "borde" and BORDE_MODE == "balanceado"
        pool_list = list(pool.order_by("id"))
        if MIN_PER_CELL:
            key = degree_key if balanced else cell_key
            picked, cells = floor_by_cell(pool_list, MIN_PER_CELL, key)
            short.extend((name, cell, n) for cell, n in cells)
            if balanced:
                chosen = {a.id for a in picked}
                picked = sorted(
                    picked + [a for a in small_sources(
                        pool_list, MIN_PER_CELL) if a.id not in chosen],
                    key=lambda a: a.id)
        elif balanced:
            picked = balanced_by_degree(pool_list, size)
        else:
            picked = spread_by_cell(pool_list, size)
        for art in picked:
            taken.add(art.id)
            sample.append((name, art))
    return sample, short


def serialize(article, stratum, manager):
    full_content, _ = manager.get_full_content(article)
    captions = [
        photo.get("caption") for photo in (article.images or [])
        if photo.get("caption")]
    return {
        "id": article.id,
        "uid": article.uid,
        "source": article.source.name,
        "section": article.section,
        "published_date": (
            article.published_date.isoformat()
            if article.published_date else None),
        "title": article.title,
        "subtitle": article.subtitle,
        "paragraphs": article.paragraphs,
        "images": captions,
        "full_content": full_content,
        "criteria": article.criteria,
        "certainty_degree": article.certainty_degree,
        "second_criteria": article.second_criteria,
        "second_certainty_degree": article.second_certainty_degree,
        "is_selected": article.is_selected,
        "discarded_reason": (
            article.discarded_reason.name
            if article.discarded_reason else None),
        "stratum": stratum,
    }


def copy_prompt_and_schema():
    from source.base_models import ArticleBase
    prompt_src = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))),
        "source/prompts/gemini_first_criteria_v3.txt")
    with open(prompt_src) as handle:
        text = handle.read()
    with open(os.path.join(OUT_DIR, "first_criteria_prompt_v3.txt"), "w") as f:
        f.write(text)
    with open(os.path.join(OUT_DIR, "first_criteria_schema.json"), "w") as f:
        json.dump(ArticleBase.model_json_schema(), f,
                  ensure_ascii=False, indent=2)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    # `FirstCriteriaManager` solo se instancia para reutilizar
    # `get_full_content`: sin `recover_record` no toca la BD ni Gemini.
    manager = FirstCriteriaManager(recover_record=None)
    sample, short = build_sample()

    by_stratum, by_source, by_year, borde_degrees = (
        Counter(), Counter(), Counter(), Counter())
    with open(OUT_FILE, "w") as handle:
        for stratum, article in sample:
            handle.write(json.dumps(
                serialize(article, stratum, manager),
                ensure_ascii=False) + "\n")
            by_stratum[stratum] += 1
            by_source[(stratum, article.source.name)] += 1
            year = (article.published_date.year
                    if article.published_date else None)
            by_year[(stratum, year)] += 1
            if stratum == "borde":
                borde_degrees[article.certainty_degree] += 1

    copy_prompt_and_schema()

    print(f"{OUT_FILE}: {sum(by_stratum.values())} artículos")
    print("por estrato:", dict(by_stratum))
    print("por estrato y fuente:", sorted(by_source.items()))
    print("por estrato y año:", sorted(
        by_year.items(), key=lambda kv: (kv[0][0], kv[0][1] or 0)))
    print("borde por certainty_degree:", sorted(borde_degrees.items()))
    vetadas = sum(n for deg, n in borde_degrees.items() if deg in (97, 98))
    print("borde vetadas (97/98):", vetadas)
    print(f"celdas por debajo del piso ({MIN_PER_CELL}):", short)


if __name__ == "__main__":
    main()
