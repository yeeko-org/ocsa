"""¿El respaldo de `geolocate_locations --fill` deshace de verdad?

Corre el backfill real sobre una muestra acotada de la base local,
lo revierte con el respaldo que dejó y compara fila por fila contra la
foto que tomó antes de empezar. Todo ocurre dentro de una transacción
que se revierte al final: la base queda como estaba, corra bien o mal.

    python .claude/diagnostics/geolocate_backup_roundtrip.py \\
        [muestra] [dictamen.csv ...]

Con CSV de dictámenes ejercita también la limpieza de comentarios: sin
ellos `comments` y `details` nunca cambian y el respaldo de esos dos
campos se quedaría sin probar.

Sale con código 1 si algo no cuadra.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from space_time.backfill import (  # noqa: E402
    BACKUP_FIELDS, Filler, Reverter, located, snapshot)
from space_time.backfill_verdicts import load_verdicts  # noqa: E402

SAMPLE = 200


def photograph(ids: list) -> dict:
    """Foto de los campos respaldables, por id de ubicación."""
    from space_time.models import Location

    rows = Location.objects.filter(pk__in=ids).prefetch_related(
        "municipalities")
    return {
        row.pk: snapshot(row, [item.pk for item in row.municipalities.all()])
        for row in rows}


def main() -> int:
    sample = int(sys.argv[1]) if len(sys.argv) > 1 else SAMPLE
    verdicts = sys.argv[2:]
    extra = list(load_verdicts(verdicts)) if verdicts else []
    ids = list(located(sample, extra_ids=extra).values_list("id", flat=True))
    backup = Path(tempfile.mkdtemp()) / "roundtrip.json"
    failures = []
    # `atomic` + `set_rollback` es lo que permite ejercitar la escritura
    # real —`bulk_update` y el `set()` del M2M— sin dejar rastro.
    with transaction.atomic():
        before = photograph(ids)
        filler = Filler(dry_run=False, limit=sample, backup=str(backup),
                        verdicts=verdicts)
        print("\n".join(filler.run()))
        after = photograph(ids)
        changed = [key for key in before if before[key] != after[key]]
        print(f"Ubicaciones que cambiaron: {len(changed)}")
        print("\n".join(Reverter(str(backup)).run()))
        restored = photograph(ids)
        for key in before:
            if before[key] != restored[key]:
                failures.append((key, before[key], restored[key]))
        transaction.set_rollback(True)
    if not changed:
        print("\nAVISO: la muestra no cambió nada; el revert no se probó.")
    for key, expected, found in failures[:10]:
        diff = [name for name in list(BACKUP_FIELDS) + ["municipalities"]
                if expected[name] != found[name]]
        print(f"  ubicación {key}: no volvió en {', '.join(diff)}")
    if failures:
        print(f"\nFALLA: {len(failures)} ubicaciones no volvieron a su "
              f"valor previo")
        return 1
    print("\nOK: todo volvió a su valor previo y la base quedó intacta")
    return 0


if __name__ == "__main__":
    sys.exit(main())
