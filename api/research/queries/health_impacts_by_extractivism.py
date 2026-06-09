"""
Afectaciones a la salud × tipo de extractivismo.

Cuenta proyectos *únicos* con al menos una afectación del tipo
"Afectaciones a la salud" (ImpactType id 11), cruzando dos variables:

  - Filas    : tipo de extractivismo del proyecto (ExtractivismType),
               vía project -> megaproject_type -> extractivism_types
               (relación Many-to-Many).
  - Columnas : subtipo de afectación (ImpactSubtype) dentro del tipo
               "salud".

Se excluye el extractivismo "Biomercantilización" (id 3) de la
visualización.

Filtros de nota (idénticos a impacts_project_coverage.py):
  - status_register público de la nota.
  - fecha de la nota <= 2024-12-31.

Reglas de conteo:
  - Un proyecto cuenta UNA sola vez por celda (extractivismo × subtipo)
    aunque tenga varias menciones/afectaciones de ese subtipo: el
    .distinct() del ORM colapsa esos duplicados antes de pandas.
  - Los totales (fila / columna / general) son UNIÓN de proyectos
    (nunique), no suma de celdas: un proyecto presente en varios
    subtipos no se duplica. Por eso los márgenes son <= a la suma de
    su fila o columna.
  - Un proyecto cuyo megaproject_type cruza varios extractivismos
    cuenta en cada fila correspondiente: es deliberado, el proyecto
    pertenece a ambas categorías.
  - La exclusión de biomercantilización se hace en pandas, no con
    queryset.exclude(): en un M2M, exclude() eliminaría el proyecto
    entero si toca ese valor, aunque también sea de otra categoría.

Salida:
  - `matrix`  : pivote limpio extractivismo × subtipo (para la gráfica).
  - `table`   : el pivote con totales por unión, para imprimir.
  - PNG de burbujas: health_impacts_by_extractivism.png (mismo dir).
"""
from pathlib import Path

import pandas as pd
from django.conf import settings
from impact.models import Impact

HEALTH_TYPE_ID = 11
EXCLUDED_EXTRACTIVISM_ID = 3  # Biomercantilización
NO_SUBTYPE_LABEL = '(Sin subtipo)'

# Mismo criterio "oficial" que impacts_project_coverage.py: solo notas
# públicas y hasta el cierre de 2024.
ONLY_PUBLIC = True


def health_pairs() -> pd.DataFrame:
    """Pares distintos (proyecto, extractivismo, subtipo) de salud.
    Una fila por combinación única. El .distinct() colapsa las
    múltiples afectaciones de un mismo proyecto, de modo que pandas
    recibe pares ya deduplicados.
    """
    qs = Impact.objects.filter(impact_type_id=HEALTH_TYPE_ID)
    if ONLY_PUBLIC:
        qs = qs.filter(
            mention__note__status_register__is_public=True,
            mention__note__date__lte='2024-12-31',
        )
    base = 'mention__project__megaproject_type__extractivism_types'
    rows = list(
        qs.values_list(
            'mention__project_id',
            f'{base}__id',
            f'{base}__short_name',
            f'{base}__name',
            f'{base}__color',
            'impact_subtype__name',
        ).distinct()
    )
    df = pd.DataFrame(rows, columns=[
        'project_id', 'extr_id', 'extr_short', 'extr_full',
        'extr_color', 'subtype_name',
    ])
    # Sin proyecto o sin extractivismo no aporta a un cruce de dos ejes.
    df = df.dropna(subset=['project_id', 'extr_id'])
    # Excluir biomercantilización a nivel fila (no con exclude(); ver
    # docstring del módulo).
    df = df[df['extr_id'] != EXCLUDED_EXTRACTIVISM_ID]
    df['subtype_name'] = df['subtype_name'].fillna(NO_SUBTYPE_LABEL)
    # Nombre corto para el eje; respaldo al nombre completo si falta.
    df['extr_name'] = df['extr_short'].fillna(df['extr_full'])
    return df


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (pairs, matrix); matrix = pivote limpio para graficar."""
    pairs = health_pairs()
    matrix = pd.pivot_table(
        pairs,
        index='extr_name',
        columns='subtype_name',
        values='project_id',
        aggfunc='nunique',
        fill_value=0,
    ).astype(int)
    # Ordena ejes por volumen de proyectos (más relevante primero).
    row_order = matrix.sum(axis=1).sort_values(ascending=False).index
    col_order = matrix.sum(axis=0).sort_values(ascending=False).index
    matrix = matrix.loc[row_order, col_order]
    return pairs, matrix


def add_margins(pairs: pd.DataFrame, matrix: pd.DataFrame) -> pd.DataFrame:
    """Agrega totales por UNIÓN de proyectos (no suma de celdas)."""
    out = matrix.copy()
    row_tot = pairs.groupby('extr_name')['project_id'].nunique()
    col_tot = pairs.groupby('subtype_name')['project_id'].nunique()
    out['Total'] = row_tot.reindex(out.index).astype(int)
    total_row = col_tot.reindex(matrix.columns)
    total_row['Total'] = pairs['project_id'].nunique()
    out.loc['Total'] = total_row.astype(int)
    return out


def plot(matrix: pd.DataFrame, path: Path,
         color_map: dict[str, str]) -> None:
    """Gráfica de burbujas: X = extractivismo, Y = subtipo, área = n.
    color_map asocia cada extractivismo con su color del catálogo.
    """
    import matplotlib
    matplotlib.use('Agg')  # backend sin ventana; solo escribe el PNG
    import matplotlib.pyplot as plt
    extrs = list(matrix.index)       # eje X
    subtypes = list(matrix.columns)  # eje Y
    xs, ys, counts, colors = [], [], [], []
    for xi, extr in enumerate(extrs):
        color = color_map.get(extr) or '#888888'  # gris si falta color
        for yi, sub in enumerate(subtypes):
            n = int(matrix.loc[extr, sub])
            if n == 0:
                continue
            xs.append(xi)
            ys.append(yi)
            counts.append(n)
            colors.append(color)  # color oficial del extractivismo (X)
    max_n = max(counts) if counts else 1
    # Área de burbuja proporcional al conteo; piso visible de 90 pt².
    areas = [90 + (c / max_n) * 2400 for c in counts]
    width = max(8, len(extrs) * 1.4)
    height = max(6, len(subtypes) * 0.5 + 2)
    fig, ax = plt.subplots(figsize=(width, height))
    ax.scatter(
        xs, ys, s=areas, c=colors, alpha=0.65,
        edgecolors='white', linewidths=1.2, zorder=3,
    )
    for x, y, c in zip(xs, ys, counts):
        ax.text(
            x, y, str(c), ha='center', va='center',
            fontsize=8, fontweight='bold', color='black', zorder=4,
        )
    ax.set_xticks(range(len(extrs)))
    ax.set_xticklabels(extrs, rotation=30, ha='right', fontsize=9)
    ax.set_yticks(range(len(subtypes)))
    ax.set_yticklabels(subtypes, fontsize=9)
    ax.set_xlabel('Tipo de extractivismo')
    ax.set_ylabel('Subtipo de afectación a la salud')
    ax.set_title(
        'Proyectos únicos con afectaciones a la salud\n'
        'por tipo de extractivismo y subtipo de afectación',
        fontsize=12,
    )
    ax.grid(True, linestyle=':', alpha=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.margins(x=0.12, y=0.04)
    ax.invert_yaxis()  # subtipo más frecuente arriba
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)


# Ruta anclada a la raíz del proyecto (settings.BASE_DIR), no a
# __file__ (ausente al correr con exec()) ni al cwd: así el guardado es
# predecible en cualquier shell. Se crea la carpeta si no existe.
_OUT_DIR = Path(settings.BASE_DIR) / 'research' / 'queries'
_OUT_DIR.mkdir(parents=True, exist_ok=True)
_PNG = (_OUT_DIR / 'health_impacts_by_extractivism.png').resolve()

pairs, matrix = build()
table = add_margins(pairs, matrix)
# Color oficial de cada extractivismo (campo color del catálogo).
color_map = (
    pairs.drop_duplicates('extr_name')
    .set_index('extr_name')['extr_color']
    .to_dict()
)
plot(matrix, _PNG, color_map)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
print('Tabla (subtipos en filas para lectura en consola):\n')
# Transpuesta: 20 subtipos como filas se leen mejor que como columnas.
print(table.T.to_string())
print(f'\nGráfica guardada en: {_PNG}')
