"""Exporta los eventos reclasificados a JSONL para la comparación jev-qwen.

Solo lectura contra la BD. No toca Gemini ni escribe nada en OCSA.

    python api/.claude/diagnostics/export_jev_sample_events.py

Universo: los `Event` que pasaron por `reclassify_legal_events`, es decir
con `reclassification_stage` no nulo (pending, reclassified, confirmed,
problematic, discarded). Si los que tienen texto de nota superan 400, se
muestrean 400 de forma determinista: se conservan íntegras las etapas
minoritarias —pending, problematic, discarded, que son toda la evidencia
de desacuerdo— y el resto se reparte entre reclassified y confirmed con
`spread()`, el muestreo disperso ya aceptado en otros diagnósticos.

El estado que se exporta es una *reconstrucción*: se reusa
`ReclassifyLegalManager.get_full_content()` con los eventos del momento
(descripción restaurada desde `reclassification_data['original']`). No se
reconstruye el bloque "EVENTOS LEGALES YA CLASIFICADOS": cuál estaba
clasificado en mayo de 2026 no es recuperable desde la BD de hoy.
"""
import json
import os
import sys
from collections import Counter, defaultdict

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from source.models import Article  # noqa: E402
from event.models import Event  # noqa: E402
from source.criteria.reclassify_legal import (  # noqa: E402
    ReclassifyLegalManager)

OUT_DIR = os.path.expanduser("~/dev/mini/jev-qwen/data/raw")
OUT_FILE = os.path.join(OUT_DIR, "events_sample.jsonl")
MAX_EVENTS = 400
KEEP_ALL_STAGES = ("pending", "problematic", "discarded")
SAMPLED_STAGES = ("reclassified", "confirmed")
SCHEMA_P_COUNT = 999


class ReplayManager(ReclassifyLegalManager):
    """Reconstruye el estado que vio Gemini para eventos ya procesados."""

    def __init__(self, events_by_note):
        super().__init__()
        self.events_by_note = events_by_note

    def _pending_events(self, article):
        return self.events_by_note.get(article.note_id, [])

    def _classified_legal_events(self, article):
        return []


def spread(items, size):
    """Muestreo determinista y disperso: evita sesgar por fecha o lote."""
    items = list(items)
    if size <= 0:
        return []
    if len(items) <= size:
        return items
    step = len(items) / size
    return [items[int(i * step)] for i in range(size)]


def original_description(event):
    data = event.reclassification_data or {}
    return (data.get("original") or {}).get("description") or event.description


def load_events():
    return list(Event.objects.filter(
        reclassification_stage__isnull=False
    ).select_related(
        "event_type", "purpose", "mention__project", "mention__note"
    ).order_by("id"))


def articles_by_note(note_ids):
    """Un artículo por nota, igual que `get_articles_objects`."""
    articles = Article.objects.filter(
        note_id__in=sorted(note_ids), paragraphs__isnull=False
    ).exclude(paragraphs=[]).order_by("note_id", "-id").distinct("note_id")
    return {art.note_id: art for art in articles}


def pick_sample(events, articles):
    """Deja fuera los eventos sin texto de nota y recorta a MAX_EVENTS."""
    usable = [ev for ev in events if ev.mention.note_id in articles]
    if len(usable) <= MAX_EVENTS:
        return usable

    by_stage = defaultdict(list)
    for event in usable:
        by_stage[event.reclassification_stage].append(event)

    picked = []
    for stage in KEEP_ALL_STAGES:
        picked.extend(by_stage.get(stage, []))

    left = MAX_EVENTS - len(picked)
    pool_total = sum(len(by_stage.get(s, [])) for s in SAMPLED_STAGES)
    assigned = 0
    for index, stage in enumerate(SAMPLED_STAGES):
        pool = by_stage.get(stage, [])
        if index == len(SAMPLED_STAGES) - 1:
            quota = left - assigned
        else:
            quota = round(left * len(pool) / pool_total)
        assigned += quota
        picked.extend(spread(pool, quota))
    return sorted(picked, key=lambda e: e.id)


def serialize(event, article, manager, contents, description):
    note_id = event.mention.note_id
    if note_id not in contents:
        contents[note_id] = manager.get_full_content(article)[0]
    data = event.reclassification_data or {}
    original = data.get("original") or {}
    ai_data = data.get("ai") or {}
    return {
        "event_id": event.id,
        "note_id": note_id,
        "article_id": article.id,
        "full_content": contents[note_id],
        "original_description": original.get("description"),
        "original_event_type": original.get("event_type"),
        "original_event_type_id": original.get("event_type_id"),
        "original_event_group_id": original.get("event_group_id"),
        "event_type": event.event_type.name if event.event_type else None,
        "purpose": event.purpose.name if event.purpose else None,
        "actual_group": ai_data.get("actual_group"),
        "reclassification_confidence": event.reclassification_confidence,
        "reclassification_stage": event.reclassification_stage,
        "description": description,
        "project": event.mention.project_id and manager._project_name(event),
        "reclassified_at": data.get("reclassified_at"),
        "paragraphs": article.paragraphs,
    }


def copy_prompt_and_schema(manager):
    api_dir = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    src = os.path.join(
        api_dir, "source/prompts/gemini_reclassify_legal_criteria_v2.txt")
    with open(src) as handle:
        text = handle.read()
    out = os.path.join(OUT_DIR, "reclassify_legal_prompt_v2.txt")
    with open(out, "w") as handle:
        handle.write(text)

    schema = manager.get_schema_class(SCHEMA_P_COUNT).model_json_schema()
    with open(os.path.join(OUT_DIR, "reclassify_legal_schema.json"),
              "w") as handle:
        json.dump(schema, handle, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT_DIR, "legal_event_types.json"), "w") as handle:
        json.dump({"catalog_block": manager._build_catalog_block()},
                  handle, ensure_ascii=False, indent=2)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    events = load_events()
    articles = articles_by_note({e.mention.note_id for e in events})
    sample = pick_sample(events, articles)

    # La descripción vigente se guarda antes de restaurar la original: el
    # bloque de eventos del prompt debe llevar la descripción que Gemini
    # vio, no la que él mismo escribió después.
    current = {e.id: e.description for e in events}
    events_by_note = defaultdict(list)
    for event in events:
        if event.mention.note_id in articles:
            event.description = original_description(event)
            events_by_note[event.mention.note_id].append(event)
    manager = ReplayManager(events_by_note)

    contents, by_stage = {}, Counter()
    with open(OUT_FILE, "w") as handle:
        for event in sample:
            article = articles[event.mention.note_id]
            record = serialize(event, article, manager, contents,
                               current[event.id])
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            by_stage[event.reclassification_stage] += 1

    copy_prompt_and_schema(manager)
    print(f"{OUT_FILE}: {sum(by_stage.values())} eventos "
          f"en {len(contents)} notas")
    print("universo con etapa:", len(events),
          "| con texto de nota:",
          len([e for e in events if e.mention.note_id in articles]))
    print("por etapa:", dict(by_stage))


if __name__ == "__main__":
    main()
