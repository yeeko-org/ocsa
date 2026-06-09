"""
Cobertura de afectaciones a nivel proyecto.

Cuántos proyectos *únicos* tienen al menos una afectación
registrada, desglosado en tres vistas:

  1. summary       — proyectos con afectación social, ambiental,
                     de ambos grupos a la vez, y de cualquier tipo.
  2. by_group      — proyectos únicos por grupo de afectación.
  3. by_type       — proyectos únicos por cada ImpactType, con su
                     grupo, para distinguir los dos conjuntos.

Reglas de conteo:
  - Un proyecto se cuenta UNA sola vez por categoría aunque tenga
    varias menciones/afectaciones de ese tipo.
  - "Cualquier afectación" es la UNIÓN de proyectos (no la suma de
    social + ambiental): un proyecto con ambas no se duplica.
  - "Afectación social y ambiental" es la INTERSECCIÓN: proyectos con
    al menos una afectación de CADA grupo.
  - El proyecto se obtiene vía la mención: Impact -> Mention ->
    Project (campo `mention__project_id`).
"""
import pandas as pd
from impact.models import Impact

# ImpactGroup tiene ids fijos en el catálogo (ver ocs-entities).
SOCIAL_GROUP_ID = 1
ECOLOGICAL_GROUP_ID = 2

# Solo afectaciones cuyo tipo está validado en el catálogo. Si se
# pone en False, entran también tipos en revisión y los conteos
# suben; déjalo en True para reproducir las cifras "oficiales".
ONLY_PUBLIC = True


def impact_project_type_pairs() -> pd.DataFrame:
    """Pares distintos (project_id, impact_type) con su grupo.
    Una fila por combinación única proyecto×tipo de afectación.
    El `.distinct()` colapsa las múltiples menciones de un mismo
    proyecto, de modo que pandas solo recibe pares ya deduplicados.
    """
    qs = Impact.objects.all()
    if ONLY_PUBLIC:
        qs = qs.filter(
            mention__note__status_register__is_public=True,
            mention__note__date__lte='2024-12-31',
        )
    rows = list(
        qs.values_list(
            'mention__project_id',
            'impact_type_id',
            'impact_type__name',
            'impact_type__impact_group_id',
            'impact_type__impact_group__name',
        ).distinct()
    )
    df = pd.DataFrame(rows, columns=[
        'project_id', 'type_id', 'type_name',
        'group_id', 'group_name',
    ])
    # Una mención sin proyecto asociado no debe contar.
    return df.dropna(subset=['project_id'])


def build() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Retorna (summary, by_group, by_type)."""
    pairs = impact_project_type_pairs()
    # -- Totales por conjunto de proyectos ----------------------
    # Conjuntos de ids: permiten unión e intersección sin duplicar.
    social_ids = set(pairs.loc[
        pairs['group_id'] == SOCIAL_GROUP_ID, 'project_id'
    ])
    eco_ids = set(pairs.loc[
        pairs['group_id'] == ECOLOGICAL_GROUP_ID, 'project_id'
    ])
    n_social = len(social_ids)
    n_eco = len(eco_ids)
    # Intersección: proyectos con AL MENOS una afectación de cada grupo.
    n_both = len(social_ids & eco_ids)
    # Unión de proyectos: cuenta distintos sobre TODAS las filas.
    n_any = pairs['project_id'].nunique()
    summary = pd.DataFrame([
        {'categoria': 'Afectación social', 'n_projects': n_social},
        {'categoria': 'Afectación ambiental', 'n_projects': n_eco},
        {'categoria': 'Afectación social y ambiental',
         'n_projects': n_both},
        {'categoria': 'Cualquier afectación', 'n_projects': n_any},
    ])
    # -- Proyectos únicos por grupo (genérico, no hardcodea) ----
    by_group = (
        pairs.groupby('group_name')['project_id']
        .nunique()
        .rename('n_projects')
        .reset_index()
        .sort_values('n_projects', ascending=False)
        .reset_index(drop=True)
    )
    # -- 4. Proyectos únicos por cada tipo, dentro de su grupo --
    by_type = (
        pairs.groupby(['group_name', 'type_name'])['project_id']
        .nunique()
        .rename('n_projects')
        .reset_index()
        .sort_values(
            ['group_name', 'n_projects'],
            ascending=[True, False],
        )
        .reset_index(drop=True)
    )
    return summary, by_group, by_type


summary, by_group, by_type = build()
