"""Verifica la política de fallos del ciclo de clasificación ([[adr-0010]]).

No llama a Gemini ni a la red: sustituye `RequestGemini` por un doble que
falla a voluntad, y revierte la transacción al terminar. Correrlo no cuesta
cuota ni deja rastro en la base.

Cubre las dos ramas duplicadas del pipeline, que hoy tienen que comportarse
igual y no comparten código ([[task-5]]).

Vive aquí por falta de suite, no por naturaleza: es un test unitario y
[[task-14]] contempla mudarlo. Mientras tanto depende de que la base local
tenga artículos, porque los toma prestados en vez de construirlos.

    python .claude/diagnostics/batch_failure_policy.py
"""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import transaction  # noqa: E402

from source.models import Article, ScrapedRecord  # noqa: E402
from source.scraper.articles import CriteriaError  # noqa: E402
from source.scraper.criteria import ManagerCriteria  # noqa: E402
from source.criteria import BaseCriteriaManager  # noqa: E402
from utils.gemini_ai import MAX_FAILED_STREAK, MIN_PENDING_FOR_CACHE  # noqa: E402

BATCH_SIZE = 30


class FakeRequest:
    """Doble de `RequestGemini` que falla siempre con la causa indicada."""

    def __init__(self, cache_lost=False):
        self.last_error = "simulado (ClientError)"
        self.last_status = None
        self.cache_lost = cache_lost
        self.cache = "cache-obj"
        self.cache_name = "diagnostic_cache"
        self.cache_seconds = 300
        self.cache_rebuilds = 0
        self.cache_disabled = False
        self.cache_error = None
        self.errors = []
        self.recreated = 0

    def recreate_cache(self, max_rebuilds=2):
        if self.cache_rebuilds >= max_rebuilds:
            self.cache = None
            self.cache_disabled = True
            return False
        self.cache_rebuilds += 1
        self.recreated += 1
        return True


def run_batch(manager, articles, fake):
    """Réplica del bucle de fallos que hoy vive duplicado en ambas ramas.

    Se copia en vez de invocar `build_criteria` porque ese método arranca
    pidiéndole artículos a la base y construyendo el request real.
    """
    len_articles = len(articles)
    failed_streak, last_status = 0, None
    for idx, article in enumerate(articles):
        try:
            manager.get_ai_criteria(article)
        except CriteriaError as e:
            failed_streak = failed_streak + 1 if e.status == last_status else 1
            last_status = e.status
            if failed_streak >= MAX_FAILED_STREAK:
                manager.abort_batch(failed_streak, last_status)
                return idx + 1
            if manager.classify_request.cache_lost:
                manager.recover_cache(len_articles - idx - 1)
            continue
        failed_streak, last_status = 0, None
    return len_articles


def run_case(name, manager_class, status_for, cache_lost, expected):
    record = ScrapedRecord.objects.filter(articles__isnull=False).first()
    articles = list(Article.objects.filter(scraped=record)[:BATCH_SIZE])
    record.errors = []
    record.save()

    manager = manager_class(recover_record=record)
    fake = FakeRequest(cache_lost=cache_lost)
    manager.classify_request = fake
    calls = {"n": 0}

    def fake_criteria(article, **kwargs):
        calls["n"] += 1
        status = status_for(calls["n"])
        if status is None:
            return
        fake.last_status = status
        raise CriteriaError(
            article, "No response AI service",
            cause=fake.last_error, status=status)

    manager.get_ai_criteria = fake_criteria
    attempted = run_batch(manager, articles, fake)
    record.refresh_from_db()

    got = {
        "attempted": attempted,
        "recreated": fake.recreated,
        "batch_errors": len(record.errors or []),
    }
    ok = all(got[k] == v for k, v in expected.items())
    print(f"  [{'ok ' if ok else 'FALLA'}] {name}")
    if not ok:
        print(f"          esperado {expected}")
        print(f"          obtenido {got}")
    return ok


CASES = [
    # Una causa que se repite es un lote condenado: se corta.
    ("misma causa siempre -> aborta al quinto",
     lambda n: "RESOURCE_EXHAUSTED", False,
     {"attempted": MAX_FAILED_STREAK, "recreated": 0, "batch_errors": 1}),
    # Causas alternadas no son un patrón: la racha nunca se acumula.
    ("causas alternadas -> no aborta",
     lambda n: "RESOURCE_EXHAUSTED" if n % 2 else "UNAVAILABLE", False,
     {"attempted": BATCH_SIZE, "recreated": 0, "batch_errors": 0}),
    # Caché irrecuperable: dos recreaciones, caída a inline reportada una
    # sola vez, y el cortacircuitos acaba cortando porque nunca se recupera.
    ("caché perdido siempre -> 2 recreaciones y un solo aviso",
     lambda n: "NOT_FOUND", True,
     {"attempted": MAX_FAILED_STREAK, "recreated": 2, "batch_errors": 2}),
    # Fallos sueltos entre éxitos: el lote tiene que terminar completo.
    ("fallo aislado cada tres -> termina el lote",
     lambda n: "UNAVAILABLE" if n % 3 == 0 else None, False,
     {"attempted": BATCH_SIZE, "recreated": 0, "batch_errors": 0}),
]


class _BaseManagerProbe(BaseCriteriaManager):
    """`BaseCriteriaManager` es abstracta; el bucle no usa sus abstractos."""

    prompt_name = "diagnostic"

    def get_articles_objects(self):
        return []

    def get_schema_class(self, p_count):
        return None

    def save_criteria_results(self, criteria, json_criteria, article):
        return None


def main():
    failures = 0
    with transaction.atomic():
        for manager_class in (ManagerCriteria, _BaseManagerProbe):
            print(f"\n{manager_class.__name__}:")
            for name, status_for, cache_lost, expected in CASES:
                if not run_case(name, manager_class, status_for,
                                cache_lost, expected):
                    failures += 1
        transaction.set_rollback(True)

    print(f"\n{'FALLAS: ' + str(failures) if failures else 'Todo en orden'}"
          " (base sin cambios: transacción revertida)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
