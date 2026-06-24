"""
Conteo de proyectos únicos por tipo de mecanismo legal (EventType
del grupo 3) y por propósito (despojo / defensa).

Genera dos tablas simples (listas de dicts, sin pandas):
  - by_type:    una fila por EventType, con proyectos únicos totales
                y desglosados en despojo / defensa.
  - by_purpose: una fila por propósito, con el nº de proyectos únicos
                que tienen al menos un evento legal de ese propósito.

Solo cuenta eventos en notas públicas y con fecha hasta DATE_CUTOFF
(mismos filtros que impacts_project_coverage.py).

Sin cruces con afectaciones ni cálculos derivados: es solo el conteo
base por tipo de evento y propósito.

Nota: total_projects NO es la suma de despojo + defensa, porque un
mismo proyecto puede tener ese tipo de evento con ambos propósitos
y se cuenta una sola vez en el total.
"""
from collections import defaultdict
from event.models import Event

# event_group_id=3 = "Mecanismos legales"; purpose 1=despojo, 2=defensa
LEGAL_GROUP_ID = 3
DESPOJO_PURPOSE_ID = 1
DEFENSA_PURPOSE_ID = 2

# Solo eventos en notas públicas y hasta la fecha de corte. En False
# entran notas no publicadas y los conteos suben; déjalo en True para
# reproducir las cifras "oficiales".
ONLY_PUBLIC = True
DATE_CUTOFF = '2024-12-31'


def legal_project_pairs() -> list[tuple]:
    """Tuplas distintas (project_id, type_id, type_name, purpose_id,
    purpose_name) de eventos del grupo legal. El `.distinct()`
    colapsa las múltiples menciones de un mismo proyecto."""
    qs = Event.objects.filter(
        event_type__event_group_id=LEGAL_GROUP_ID,
        purpose__isnull=False,
    )
    if ONLY_PUBLIC:
        qs = qs.filter(
            mention__note__status_register__is_public=True,
            mention__note__date__lte=DATE_CUTOFF,
        )
    rows = list(
        qs.values_list(
            'mention__project_id',
            'event_type_id',
            'event_type__name',
            'purpose_id',
            'purpose__name',
        ).distinct()
    )
    # Una mención sin proyecto asociado no debe contar.
    return [r for r in rows if r[0] is not None]


def build() -> tuple[list[dict], list[dict]]:
    """Retorna (by_type, by_purpose)."""
    pairs = legal_project_pairs()
    # -- Proyectos únicos por EventType, desglosados por propósito --
    # Sets de project_id: el len() final da el conteo sin duplicar.
    total = defaultdict(set)
    despojo = defaultdict(set)
    defensa = defaultdict(set)
    type_name = {}
    purpose_sets = defaultdict(set)
    for proj_id, type_id, tname, purpose_id, pname in pairs:
        type_name[type_id] = tname
        total[type_id].add(proj_id)
        if purpose_id == DESPOJO_PURPOSE_ID:
            despojo[type_id].add(proj_id)
        elif purpose_id == DEFENSA_PURPOSE_ID:
            defensa[type_id].add(proj_id)
        purpose_sets[pname].add(proj_id)
    by_type = sorted(
        (
            {
                'event_type': type_name[type_id],
                'total_projects': len(total[type_id]),
                'despojo_projects': len(despojo[type_id]),
                'defensa_projects': len(defensa[type_id]),
            }
            for type_id in total
        ),
        key=lambda row: row['total_projects'],
        reverse=True,
    )
    # -- Proyectos únicos por propósito (unión sobre todos los tipos)
    by_purpose = sorted(
        (
            {'purpose': pname, 'n_projects': len(proj_ids)}
            for pname, proj_ids in purpose_sets.items()
        ),
        key=lambda row: row['n_projects'],
        reverse=True,
    )
    return by_type, by_purpose


by_type, by_purpose = build()