"""Corrida en seco de la cadena del catálogo del INPI sobre la base que diga
DATABASE_NAME: load_inpi_catalog → tidy_indigenous_groups →
merge_indigenous_groups, en una sola transacción que se revierte al final.

El --dry-run de cada comando revierte su propia transacción, así que la
fusión en seco no vería lo que cargó la carga en seco; aquí corren sin la
bandera dentro de una transacción exterior. Después repite la cadena para
mostrar que la segunda pasada no cambia nada, e imprime el estado final.

    DATABASE_NAME=ocsa-prod-20261108 DATABASE_LEGACY_NAME=ocsa-prod-20261108 \
        python api/.claude/diagnostics/inpi_chain_dry_run.py
"""
import os
import sys
from io import StringIO

import django

BASE = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.management import call_command  # noqa: E402
from django.db import transaction  # noqa: E402
from django.db.models import Count  # noqa: E402

from actor.models import Actor  # noqa: E402
from classify.models import IndigenousGroup  # noqa: E402

CHAIN = ["load_inpi_catalog", "tidy_indigenous_groups",
         "merge_indigenous_groups"]


class Rollback(Exception):
    pass


def counts():
    return {g.id: (g.name.strip(), g.n) for g in
            IndigenousGroup.objects.annotate(n=Count("actors"))}


def snapshot():
    return list(IndigenousGroup.objects.order_by("id").values_list(
        "id", "name", "alternative_names", "is_official",
        "status_validation_id", "comments")), list(
        Actor.objects.filter(indigenous_group__isnull=False).order_by(
            "id").values_list("id", "indigenous_group_id", "comments"))


def run(command):
    out = StringIO()
    call_command(command, stdout=out)
    return out.getvalue()


def main():
    before = counts()
    try:
        with transaction.atomic():
            for command in CHAIN:
                print(f"\n===== {command}\n")
                print(run(command), end="")
            first = snapshot()
            print("\n===== segunda pasada (idempotencia)\n")
            for command in CHAIN:
                print(f"--- {command}: " + run(command).strip().splitlines()[-1])
            print("estado idéntico tras la segunda pasada:",
                  snapshot() == first)
            report(before)
            raise Rollback
    except Rollback:
        print("\n[revertido: la base queda como estaba]")


def report(before):
    after = counts()
    groups = IndigenousGroup.objects.annotate(n=Count("actors"))
    official = groups.filter(is_official=True).order_by("name")
    print("\n===== Entradas oficiales "
          f"({official.count()})\n")
    for g in official:
        states = ", ".join(s.short_name or s.name for s in g.states.all())
        print(f"#{g.id} {g.name} | {g.n} actores | {states}")
    print("\n===== Entradas no oficiales que quedan\n")
    for g in groups.filter(is_official=False).order_by("id"):
        print(f"#{g.id} «{g.name.strip()}» | {g.status_validation_id} | "
              f"{g.n} actores")
    print("\n===== Pueblos oficiales sin actor\n")
    print(", ".join(g.name for g in official if not g.n))
    print("\n===== Actores por entrada, antes → después\n")
    for gid in sorted(set(before) | set(after)):
        name, n_before = before.get(gid, (after[gid][0], 0))
        n_after = after.get(gid, (name, 0))[1]
        new_name = after.get(gid, (name, 0))[0]
        if n_before or n_after:
            label = name if name == new_name else f"{name} → {new_name}"
            print(f"#{gid} {label}: {n_before} → {n_after}")
    total_b = sum(n for _, n in before.values())
    total_a = sum(n for _, n in after.values())
    print(f"\nactores con pueblo: {total_b} → {total_a}")
    for actor_id in (6374, 4822, 4760, 7583, 2851):
        actor = Actor.objects.select_related("indigenous_group").get(
            id=actor_id)
        print(f"\nactor {actor_id} → #{actor.indigenous_group_id} "
              f"{actor.indigenous_group}\n{actor.comments}")


main()
