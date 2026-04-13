# ============================================================
# Co-ocurrencia: mecanismos legales x afectaciones
# ============================================================
# Dos análisis:
#   1. Mecanismos de despojo  x Afectaciones
#   2. Mecanismos de defensa  x Afectaciones
#
# Cada analisis produce:
#   - $crudo : conteo de proyectos por par (mecanismo,
#              afectacion)
#   - $lift  : lift = P(afectación | mecanismo) / P(afectación)
#       > 1 -> la combinación ocurre MÁS de lo esperado
#       < 1 -> ocurre MENOS de lo esperado
#
# Las afectaciones se etiquetan "Grupo | Tipo".
# ============================================================

source("config.R")
con <- conectar_bd()

# ---- Función principal -------------------------------------

analisis_legal_impactos <- function(
    con,
    purpose_id,
    min_mechanism_projects = 4,
    min_impact_projects = 3
) {

  # 1. Mecanismos legales con suficientes proyectos
  sql_mechs <- sprintf("
    SELECT
        et.id,
        et.name,
        COUNT(DISTINCT m.project_id) AS n_projects
    FROM event_eventtype et
    JOIN event_event ev   ON ev.event_type_id = et.id
    JOIN source_mention m ON ev.mention_id = m.id
    WHERE et.event_group_id = 3
      AND ev.purpose_id = %d
    GROUP BY et.id, et.name
    HAVING COUNT(DISTINCT m.project_id) >= %d
    ORDER BY n_projects DESC
  ", purpose_id, min_mechanism_projects)

  mecanismos <- consulta(con, sql_mechs)

  # 2. Tipos de afectación validados con suficientes proyectos
  sql_impacts <- sprintf("
    SELECT
        it.id,
        it.name,
        ig.name AS group_name,
        COUNT(DISTINCT m.project_id) AS n_projects
    FROM impact_impacttype it
    JOIN impact_impactgroup ig ON it.impact_group_id = ig.id
    JOIN impact_impact i       ON i.impact_type_id = it.id
    JOIN source_mention m      ON i.mention_id = m.id
    WHERE it.status_validation_id = 'validated'
    GROUP BY it.id, it.name, ig.name
    HAVING COUNT(DISTINCT m.project_id) >= %d
    ORDER BY ig.name, n_projects DESC
  ", min_impact_projects)

  tipos_afectacion <- consulta(con, sql_impacts)

  # 3. Total de proyectos con al menos un evento o afectación
  sql_total <- "
    SELECT COUNT(DISTINCT project_id) AS total
    FROM (
        SELECT m.project_id
        FROM source_mention m
        JOIN event_event ev ON ev.mention_id = m.id
        UNION
        SELECT m.project_id
        FROM source_mention m
        JOIN impact_impact i ON i.mention_id = m.id
    ) sub
  "
  total_projects <- consulta(con, sql_total)$total

  # 4. Pares (proyecto, mecanismo) para el propósito dado
  sql_mech_pairs <- sprintf("
    SELECT DISTINCT
        m.project_id,
        ev.event_type_id AS mech_type_id
    FROM event_event ev
    JOIN source_mention m ON ev.mention_id = m.id
    JOIN event_eventtype et ON ev.event_type_id = et.id
    WHERE et.event_group_id = 3
      AND ev.purpose_id = %d
  ", purpose_id)

  mech_pairs <- consulta(con, sql_mech_pairs)

  # 5. Pares (proyecto, tipo de afectación)
  sql_impact_pairs <- "
    SELECT DISTINCT
        m.project_id,
        i.impact_type_id
    FROM impact_impact i
    JOIN source_mention m ON i.mention_id = m.id
  "
  impact_pairs <- consulta(con, sql_impact_pairs)

  # ---- Cálculo de co-ocurrencia ----------------------------

  # Etiquetas: "Grupo | Tipo"
  etiquetas <- tipos_afectacion |>
    mutate(label = paste(group_name, name, sep = " | "))

  # Merge: proyectos que tienen mecanismo Y afectacion
  cooc <- mech_pairs |>
    inner_join(impact_pairs, by = "project_id") |>
    # Filtrar solo los tipos que pasaron los umbrales
    filter(
      mech_type_id %in% mecanismos$id,
      impact_type_id %in% tipos_afectacion$id
    ) |>
    group_by(mech_type_id, impact_type_id) |>
    summarise(n_projects = n_distinct(project_id),
              .groups = "drop")

  # Mapear nombres
  cooc <- cooc |>
    left_join(mecanismos |> select(id, name),
              by = c("mech_type_id" = "id")) |>
    rename(mecanismo = name) |>
    left_join(etiquetas |> select(id, label),
              by = c("impact_type_id" = "id")) |>
    rename(afectacion = label)

  # Pivot: filas = mecanismo, columnas = afectacion
  # Ordenar columnas por grupo
  col_order <- etiquetas$label[
    etiquetas$label %in% unique(cooc$afectacion)
  ]

  df_crudo <- cooc |>
    select(mecanismo, afectacion, n_projects) |>
    pivot_wider(
      names_from = afectacion,
      values_from = n_projects,
      values_fill = 0
    )

  # Reordenar columnas según grupo
  cols_presentes <- intersect(col_order, names(df_crudo))
  df_crudo <- df_crudo |>
    select(mecanismo, all_of(cols_presentes))

  # ---- Cálculo de lift -------------------------------------

  # P(afectación) = proyectos con esa afectación / total
  baseline_afectacion <- impact_pairs |>
    filter(impact_type_id %in% tipos_afectacion$id) |>
    group_by(impact_type_id) |>
    summarise(n = n_distinct(project_id), .groups = "drop") |>
    left_join(etiquetas |> select(id, label),
              by = c("impact_type_id" = "id")) |>
    mutate(p_base = n / total_projects) |>
    select(label, p_base) |>
    deframe()

  # Proyectos por mecanismo
  proj_por_mech <- mech_pairs |>
    filter(mech_type_id %in% mecanismos$id) |>
    group_by(mech_type_id) |>
    summarise(n = n_distinct(project_id), .groups = "drop") |>
    left_join(mecanismos |> select(id, name),
              by = c("mech_type_id" = "id")) |>
    select(name, n) |>
    deframe()

  # Calcular lift por celda
  df_lift <- df_crudo
  for (col in cols_presentes) {
    n_mech <- proj_por_mech[df_lift$mecanismo]
    p_given_mech <- df_lift[[col]] / n_mech
    p_base <- baseline_afectacion[col]
    df_lift[[col]] <- round(
      ifelse(p_base > 0, p_given_mech / p_base, 0),
      2
    )
  }

  list(
    crudo       = df_crudo,
    lift        = df_lift,
    mecanismos  = mecanismos,
    afectaciones = tipos_afectacion
  )
}

# ============================================================
# 1. Despojo x Afectaciones
# ============================================================
cat("\n=== Despojo x Afectaciones ===\n")
despojo <- analisis_legal_impactos(
  con,
  purpose_id = 1,
  min_mechanism_projects = 4,
  min_impact_projects = 3
)
cat("\nConteo bruto:\n")
print(despojo$crudo)
cat("\nLift:\n")
print(despojo$lift)

# ============================================================
# 2. Defensa x Afectaciones
# ============================================================
cat("\n=== Defensa x Afectaciones ===\n")
defensa <- analisis_legal_impactos(
  con,
  purpose_id = 2,
  min_mechanism_projects = 4,
  min_impact_projects = 3
)
cat("\nConteo bruto:\n")
print(defensa$crudo)
cat("\nLift:\n")
print(defensa$lift)

dbDisconnect(con)
