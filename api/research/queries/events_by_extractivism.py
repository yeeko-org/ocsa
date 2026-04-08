"""
Mecanismos legales cruzados con tipo de extractivismo.
Genera tres DataFrames:
  - df_extractivism: total de proyectos por tipo de extractivismo
  - df_events_extr: pivot de EventType × ExtractivismType con conteos
  - df_purpose_extr: pivot de Purpose × ExtractivismType con totales
"""
import pandas as pd
from django.db.models import Count, Q, F
from event.models import EventType, Event
from project.models import ExtractivismType


# Base: total de proyectos por tipo de extractivismo
projects_by_extractivism = list(
    ExtractivismType.objects
    .annotate(
        total_projects=Count(
            'megaproject_types__projects',
            distinct=True,
        ),
    )
    .values('id', 'name', 'total_projects')
    .order_by('-total_projects')
)
df_extractivism = pd.DataFrame(projects_by_extractivism)

# Mecanismos legales × extractivismo: conteo de proyectos
events_extractivism = list(
    EventType.objects
    .filter(event_group_id=3)
    .values(
        'id', 'name',
        extractivism_type=F(
            'events__mention__project'
            '__megaproject_type__extractivism_types__name'),
    )
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
    .order_by('name', '-project_count')
)

df_events_extr = pd.DataFrame(events_extractivism)
df_events_extr['extractivism_type'] = (
    df_events_extr['extractivism_type'].str[:25])

df_events_extr = (
    df_events_extr
    .pivot_table(
        index='name',
        columns='extractivism_type',
        values=['project_count', 'despojo_count', 'defensa_count'],
        fill_value=0,
    )
)
# Aplanar MultiIndex de columnas: "project_count | Minería"
df_events_extr.columns = [
    f'{val} | {ext}' for val, ext in df_events_extr.columns
]
df_events_extr = df_events_extr.reset_index()

# Propósito (despojo/defensa) × extractivismo con totales

purpose_extractivism = list(
    Event.objects
    .filter(event_type__event_group_id=3, purpose__isnull=False)
    .values(
        purpose_name=F('purpose__name'),
        extractivism_type=F(
            'mention__project'
            '__megaproject_type__extractivism_types__name'),
    )
    .annotate(
        project_count=Count(
            'mention__project',
            distinct=True,
        ),
    )
    .order_by('purpose_name', '-project_count')
)

df_purpose_extr = (
    pd.DataFrame(purpose_extractivism)
    .pivot_table(
        index='extractivism_type',
        columns='purpose_name',
        values='project_count',
        fill_value=0,
    )
    .reset_index()
    .merge(
        df_extractivism[['name', 'total_projects']],
        left_on='extractivism_type',
        right_on='name',
        how='left',
    )
    .drop(columns=['name'])
    .sort_values('total_projects', ascending=False)
)