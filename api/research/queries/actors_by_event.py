"""
Actores involucrados en mecanismos legales (event_group_id=3).
Genera dos DataFrames:
  - df_event_types: conteo de proyectos por tipo de mecanismo legal
    (total, despojo, defensa)
  - df_actors / df_grouped: actores con sus mecanismos y conteos,
    enriquecidos con totales del tipo de evento
"""
import pandas as pd
from actor.models import Actor
from django.db.models import Count, Q, F
from event.models import EventType

# Proyectos por tipo de mecanismo legal (despojo vs defensa)
projects_by_event_type = list(
    EventType.objects
    .filter(event_group_id=3)
    .annotate(
        project_count=Count(
            'events__mention__project',
            distinct=True,
        ),
        despojo_count=Count(
            'events__mention__project',
            filter=Q(events__purpose_id=1),
            distinct=True,
        ),
        defensa_count=Count(
            'events__mention__project',
            filter=Q(events__purpose_id=2),
            distinct=True,
        ),
    )
    .values('id', 'name',
           'project_count', 'despojo_count', 'defensa_count')
    .order_by('-project_count')
)
df_event_types = pd.DataFrame(projects_by_event_type)

# Actores con sus tipos de mecanismo y conteos por propósito
actors_mecanismos = list(
    Actor.objects
    .filter(
        participants__mention__events__event_type__event_group_id=3
    )
    .values(
        'id', 'name', 'alternative_names',
        event_type=F(
            'participants__mention__events__event_type__name'),
    )
    .annotate(
        project_count=Count(
            'participants__mention__project',
            distinct=True,
        ),
        despojo_count=Count(
            'participants__mention__project',
            filter=Q(
                participants__mention__events__purpose_id=1),
            distinct=True,
        ),
        defensa_count=Count(
            'participants__mention__project',
            filter=Q(
                participants__mention__events__purpose_id=2),
            distinct=True,
        ),
    )
    .order_by('-project_count')
)

df_actors = pd.DataFrame(actors_mecanismos)

# Enriquecer actores con totales globales del tipo de evento
df_actors_full = df_actors.merge(
    df_event_types.rename(columns={
        'project_count': 'total_projects',
        'despojo_count': 'total_despojo',
        'defensa_count': 'total_defensa',
    }),
    left_on='event_type', right_on='name',
    how='left',
    suffixes=('', '_et'),
).drop(columns=['id_et', 'name_et'])

# Agrupar actores: un renglón por actor con sus mecanismos concatenados
df_grouped = (
    df_actors
    .groupby(['id', 'name', 'alternative_names'])
    .agg(
        event_types=('event_type', lambda x: ', '.join(
            sorted(x.unique()))),
        project_count=('project_count', 'sum'),
        despojo_count=('despojo_count', 'sum'),
        defensa_count=('defensa_count', 'sum'),
    )
    .reset_index()
    .sort_values('project_count', ascending=False)
)
