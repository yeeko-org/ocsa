"""
Co-ocurrencia entre mecanismos legales y afectaciones (sociales
y ambientales) a nivel proyecto.

Dos análisis:
  1. Mecanismos de despojo × Afectaciones
  2. Mecanismos de defensa × Afectaciones

Cada análisis produce:
  - df_raw: conteo de proyectos por par (mecanismo, afectación)
  - df_lift: lift = P(afectación | mecanismo) / P(afectación)
    > 1 → concurrencia más frecuente de lo esperado (atípica+)
    < 1 → concurrencia menos frecuente de lo esperado (atípica-)

Las afectaciones se etiquetan como "ImpactGroup | ImpactType".
"""
import pandas as pd
from django.db.models import Count, Q, F
from event.models import Event, EventType
from impact.models import Impact, ImpactType


class LegalImpactCooccurrence:
    """Lift entre mecanismos legales (por propósito) y tipos de
    afectación a nivel proyecto.

    Lift = P(impact_type | mecanismo) / P(impact_type)
    """

    LEGAL_GROUP_ID = 3
    MIN_IMPACTS = 10

    def __init__(
        self,
        purpose_id: int,
        min_mechanism_projects: int = 4,
        min_impact_projects: int = 3,
    ):
        self.purpose_id = purpose_id
        self.min_mechanism_projects = min_mechanism_projects
        self.min_impact_projects = min_impact_projects

        self._mechanisms = self._fetch_mechanisms()
        self._impact_types = self._fetch_impact_types()
        self._total_projects = self._count_total_projects()

    # -- Queries ORM -------------------------------------------------

    def _fetch_mechanisms(self) -> pd.DataFrame:
        """EventTypes legales con ≥ min_mechanism_projects proyectos
        para el propósito dado."""
        rows = list(
            EventType.objects
            .filter(event_group_id=self.LEGAL_GROUP_ID)
            .annotate(
                n_projects=Count(
                    'events__mention__project',
                    filter=Q(events__purpose_id=self.purpose_id),
                    distinct=True,
                ),
            )
            .filter(n_projects__gte=self.min_mechanism_projects)
            .values('id', 'name', 'n_projects')
            .order_by('-n_projects')
        )
        return pd.DataFrame(rows)

    def _fetch_impact_types(self) -> pd.DataFrame:
        """ImpactTypes con ≥ min_impact_projects proyectos,
        etiquetados con su grupo."""
        rows = list(
            ImpactType.objects
            .filter(
                status_validation__name='validated',
            )
            .annotate(
                n_projects=Count(
                    'impact__mention__project',
                    distinct=True,
                ),
                group_name=F('impact_group__name'),
            )
            .filter(n_projects__gte=self.min_impact_projects)
            .values('id', 'name', 'group_name', 'n_projects')
            .order_by('group_name', '-n_projects')
        )
        return pd.DataFrame(rows)

    def _count_total_projects(self) -> int:
        """Proyectos con al menos un evento o una afectación."""
        from source.models import Mention
        return (
            Mention.objects
            .filter(
                Q(events__isnull=False)
                | Q(impacts__isnull=False)
            )
            .values('project_id')
            .distinct()
            .count()
        )

    def _mechanism_project_pairs(self) -> pd.DataFrame:
        """Pares (project_id, mech_type_id) para mecanismos del
        propósito dado."""
        pairs = list(
            Event.objects
            .filter(
                event_type__event_group_id=self.LEGAL_GROUP_ID,
                purpose_id=self.purpose_id,
            )
            .values_list(
                'mention__project_id', 'event_type_id',
            )
            .distinct()
        )
        return pd.DataFrame(
            pairs, columns=['project_id', 'mech_type_id'],
        )

    def _impact_project_pairs(self) -> pd.DataFrame:
        """Pares (project_id, impact_type_id) de afectaciones."""
        pairs = list(
            Impact.objects
            .values_list(
                'mention__project_id', 'impact_type_id',
            )
            .distinct()
        )
        return pd.DataFrame(
            pairs, columns=['project_id', 'impact_type_id'],
        )

    # -- Cálculo de co-ocurrencia ------------------------------------

    def build(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Retorna (df_raw, df_lift).

        df_raw: filas = mecanismos, columnas = afectaciones,
                valores = nº de proyectos con ambos.
        df_lift: misma forma, valores = lift.
        """
        mech_pairs = self._mechanism_project_pairs()
        impact_pairs = self._impact_project_pairs()

        # Merge: proyectos que tienen mecanismo Y afectación
        merged = mech_pairs.merge(impact_pairs, on='project_id')

        cooc = (
            merged
            .groupby(['mech_type_id', 'impact_type_id'])
            ['project_id']
            .nunique()
            .reset_index()
            .rename(columns={'project_id': 'n_projects'})
        )

        # Mapear nombres
        mech_names = dict(
            zip(self._mechanisms['id'], self._mechanisms['name'])
        )
        impact_labels = dict(zip(
            self._impact_types['id'],
            self._impact_types['group_name']
            + ' | '
            + self._impact_types['name'],
        ))

        cooc['mecanismo'] = cooc['mech_type_id'].map(mech_names)
        cooc['afectacion'] = (
            cooc['impact_type_id'].map(impact_labels)
        )

        # Filtrar solo los tipos que pasaron los umbrales
        cooc = cooc.dropna(subset=['mecanismo', 'afectacion'])

        # Pivot: filas = mecanismo, columnas = afectación
        df_raw = cooc.pivot_table(
            index='mecanismo',
            columns='afectacion',
            values='n_projects',
            fill_value=0,
        )

        # Ordenar columnas por grupo (ya vienen ordenadas por
        # group_name en _fetch_impact_types)
        ordered_cols = [
            label for label in impact_labels.values()
            if label in df_raw.columns
        ]
        df_raw = df_raw[ordered_cols]

        # Baseline: P(impact_type) = proyectos con ese tipo / total
        valid_ids = set(self._impact_types['id'])
        impact_proj_counts = (
            impact_pairs[
                impact_pairs['impact_type_id'].isin(valid_ids)
            ]
            .groupby('impact_type_id')
            ['project_id']
            .nunique()
        )
        impact_baseline = impact_proj_counts.rename(
            index=impact_labels,
        ) / self._total_projects

        # Proyectos por mecanismo
        valid_mech_ids = set(self._mechanisms['id'])
        mech_proj_counts = (
            mech_pairs[
                mech_pairs['mech_type_id'].isin(valid_mech_ids)
            ]
            .groupby('mech_type_id')
            ['project_id']
            .nunique()
            .rename(index=mech_names)
        )

        # Lift por celda
        df_lift = df_raw.copy().astype(float)
        for mech in df_lift.index:
            n_mech = mech_proj_counts.get(mech, 1)
            for impact_col in df_lift.columns:
                p_given_mech = (
                    df_lift.loc[mech, impact_col] / n_mech
                )
                p_baseline = impact_baseline.get(impact_col, 1)
                df_lift.loc[mech, impact_col] = (
                    round(p_given_mech / p_baseline, 2)
                    if p_baseline > 0
                    else 0.0
                )

        return df_raw, df_lift

    @property
    def mechanisms(self) -> pd.DataFrame:
        return self._mechanisms

    @property
    def impact_types(self) -> pd.DataFrame:
        return self._impact_types


# ================================================================
# 1. Despojo × Afectaciones
# ================================================================
despojo = LegalImpactCooccurrence(
    purpose_id=1,
    min_mechanism_projects=4,
    min_impact_projects=3,
)
df_despojo_raw, df_despojo_lift = despojo.build()

# ================================================================
# 2. Defensa × Afectaciones
# ================================================================
defensa = LegalImpactCooccurrence(
    purpose_id=2,
    min_mechanism_projects=4,
    min_impact_projects=3,
)
df_defensa_raw, df_defensa_lift = defensa.build()