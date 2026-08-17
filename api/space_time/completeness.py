"""Completitud de una `Location` y su lectura frente al status.

«Completa» es un hecho verificable —entidad, municipio y geometría—,
mientras que el status de ubicación lo fija una persona. Cruzar ambas
cosas es lo que hace visible el trabajo pendiente: completas que nadie
promovió, incompletas que nadie ha tocado, y aprobadas que en realidad
no lo están.

Las Q de este módulo se evalúan siempre sobre `Location`; a nivel de
proyecto se aplican con una subconsulta (`locations__in=...`) para que
las condiciones caigan sobre la misma ubicación y para no negar a
través de una relación múltiple.
"""

from __future__ import annotations

from django.db.models import Q

from space_time.geometry import has_geometry_q, no_geometry_q

# Status que expresan un juicio humano ya emitido: promoverlos o
# corregirlos no es automatizable, así que quedan fuera del pendiente.
HUMAN_JUDGEMENT_STATUSES = (
    "finished", "Aproximado", "need_consensus", "filled")

APPROVED_STATUSES = ("finished", "Aproximado")

COMPLETE_UNPROMOTED = "complete_unpromoted"
INCOMPLETE_UNPROMOTED = "incomplete_unpromoted"
APPROVED_INCOMPLETE = "approved_incomplete"


def complete_q() -> Q:
    """Entidad, municipio y geometría presentes."""
    return (
        Q(state__isnull=False)
        & Q(municipality__isnull=False)
        & has_geometry_q())


def incomplete_q() -> Q:
    """Negación de `complete_q` en forma positiva."""
    return (
        Q(state__isnull=True)
        | Q(municipality__isnull=True)
        | no_geometry_q())


def no_judgement_q() -> Q:
    """Status sin juicio humano emitido, incluido el nulo.

    El nulo se nombra aparte porque `NOT IN` no lo alcanza en SQL.
    """
    return (
        Q(status_location__isnull=True)
        | ~Q(status_location__in=HUMAN_JUDGEMENT_STATUSES))


def completeness_q(bucket: str) -> Q | None:
    """Q sobre `Location` del bucket pedido, o `None` si no existe."""
    if bucket == COMPLETE_UNPROMOTED:
        return complete_q() & no_judgement_q()
    if bucket == INCOMPLETE_UNPROMOTED:
        return incomplete_q() & no_judgement_q()
    if bucket == APPROVED_INCOMPLETE:
        return Q(status_location__in=APPROVED_STATUSES) & incomplete_q()
    return None
