"""
Co-ocurrencia entre mecanismos legales y eventos de oposición.
Dos análisis:
  1. Mecanismos de despojo × Violencias
  2. Mecanismos de defensa × Acciones colectivas

Cada análisis produce:
  - df_raw: conteo bruto de proyectos por par (mecanismo, evento)
  - df_lift: qué tan más/menos frecuente es cada evento cuando
    hay un mecanismo dado, comparado con su frecuencia global
"""
import pandas as pd
from django.db.models import Count, Q
from event.models import Event, EventType


class CooccurrenceAnalysis:
    """Calcula co-ocurrencia y lift entre mecanismos legales
    y un grupo de eventos opuestos a nivel proyecto.

    Lift = P(oposición | mecanismo) / P(oposición)
    - lift > 1 → la oposición ocurre más de lo esperado
    - lift < 1 → ocurre menos de lo esperado
    """

    LEGAL_GROUP_ID = 3
    MIN_EVENTS = 20

    def __init__(
        self,
        purpose_id: int,
        opposition_group_id: int,
        min_mechanism_projects: int = 4,
    ):
        self.purpose_id = purpose_id
        self.opposition_group_id = opposition_group_id
        self.min_mechanism_projects = min_mechanism_projects

        self._mechanisms = self._fetch_mechanisms()
        self._oppositions = self._fetch_oppositions()
        self._total_projects = self._count_total_projects()

    # -- Queries ORM -------------------------------------------------

    def _project_type_pairs(
        self, group_id: int, purpose_id: int | None = None,
    ) -> list[tuple[int, int]]:
        """Pares (project_id, event_type_id) para un grupo/propósito."""
        qs = Event.objects.filter(
            event_type__event_group_id=group_id,
        )
        if purpose_id is not None:
            qs = qs.filter(purpose_id=purpose_id)
        return list(
            qs.values_list(
                'mention__project_id', 'event_type_id',
            ).distinct()
        )

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

    def _fetch_oppositions(self) -> pd.DataFrame:
        """EventTypes del grupo opuesto con ≥ MIN_EVENTS eventos."""
        rows = list(
            EventType.objects
            .filter(event_group_id=self.opposition_group_id)
            .annotate(n_events=Count('events'))
            .filter(n_events__gte=self.MIN_EVENTS)
            .values('id', 'name', 'n_events')
            .order_by('-n_events')
        )
        return pd.DataFrame(rows)

    def _count_total_projects(self) -> int:
        """Total de proyectos con al menos un evento (universo)."""
        from source.models import Mention
        return (
            Mention.objects
            .filter(events__isnull=False)
            .values('project_id')
            .distinct()
            .count()
        )

    # -- Cálculo de co-ocurrencia ------------------------------------

    def build(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Retorna (df_raw, df_lift).

        df_raw: filas = mecanismos, columnas = oposiciones, valores
                = nº de proyectos que tienen ambos.
        df_lift: misma forma, valores = lift.
        """
        # Pares (project, event_type) para cada lado
        mech_pairs = pd.DataFrame(
            self._project_type_pairs(
                self.LEGAL_GROUP_ID, self.purpose_id,
            ),
            columns=['project_id', 'mech_type_id'],
        )
        opp_pairs = pd.DataFrame(
            self._project_type_pairs(
                self.opposition_group_id,
            ),
            columns=['project_id', 'opp_type_id'],
        )

        # Merge por project_id: solo proyectos que tienen ambos
        merged = mech_pairs.merge(opp_pairs, on='project_id')

        # Conteo de proyectos por par (mecanismo, oposición)
        cooccurrence = (
            merged
            .groupby(['mech_type_id', 'opp_type_id'])
            ['project_id']
            .nunique()
            .reset_index()
            .rename(columns={'project_id': 'n_projects'})
        )

        # Mapear nombres
        mech_names = dict(
            zip(self._mechanisms['id'], self._mechanisms['name'])
        )
        opp_names = dict(
            zip(self._oppositions['id'], self._oppositions['name'])
        )

        cooccurrence['mecanismo'] = (
            cooccurrence['mech_type_id'].map(mech_names)
        )
        cooccurrence['oposicion'] = (
            cooccurrence['opp_type_id'].map(opp_names)
        )

        # Filtrar solo los tipos que pasaron los umbrales
        cooccurrence = cooccurrence.dropna(
            subset=['mecanismo', 'oposicion']
        )

        # Pivot: filas = mecanismo, columnas = oposición
        df_raw = cooccurrence.pivot_table(
            index='mecanismo',
            columns='oposicion',
            values='n_projects',
            fill_value=0,
        )

        # Baseline: P(oposición) = proyectos con esa oposición / total
        opp_project_counts = (
            opp_pairs[opp_pairs['opp_type_id'].isin(
                self._oppositions['id']
            )]
            .groupby('opp_type_id')
            ['project_id']
            .nunique()
        )
        opp_baseline = opp_project_counts.rename(
            index=opp_names
        ) / self._total_projects

        # Proyectos por mecanismo (para el propósito dado)
        mech_project_counts = (
            mech_pairs[mech_pairs['mech_type_id'].isin(
                self._mechanisms['id']
            )]
            .groupby('mech_type_id')
            ['project_id']
            .nunique()
            .rename(index=mech_names)
        )

        # Lift por celda
        df_lift = df_raw.copy().astype(float)
        for mech in df_lift.index:
            n_mech = mech_project_counts.get(mech, 1)
            for opp in df_lift.columns:
                p_opp_given_mech = df_lift.loc[mech, opp] / n_mech
                p_opp = opp_baseline.get(opp, 1)
                df_lift.loc[mech, opp] = round(
                    p_opp_given_mech / p_opp, 2
                ) if p_opp > 0 else 0.0

        return df_raw, df_lift

    @property
    def mechanisms(self) -> pd.DataFrame:
        return self._mechanisms

    @property
    def oppositions(self) -> pd.DataFrame:
        return self._oppositions


# ================================================================
# 1. Despojo × Violencias
# ================================================================
despojo = CooccurrenceAnalysis(
    purpose_id=1,              # despojo
    opposition_group_id=1,     # violencias
    min_mechanism_projects=4,
)
df_despojo_raw, df_despojo_lift = despojo.build()

# ================================================================
# 2. Defensa × Acciones colectivas
# ================================================================
defensa = CooccurrenceAnalysis(
    purpose_id=2,              # defensa
    opposition_group_id=2,     # acciones colectivas
    min_mechanism_projects=4,
)
df_defensa_raw, df_defensa_lift = defensa.build()
