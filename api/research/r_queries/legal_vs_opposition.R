# ============================================================
# Co-ocurrencia: mecanismos legales x eventos de oposicion
# ============================================================
# Dos analisis:
#   1. Mecanismos de despojo  x Violencias
#   2. Mecanismos de defensa  x Acciones colectivas
#
# Cada analisis produce:
#   - $crudo : conteo de proyectos por par (mecanismo, evento)
#   - $lift  : lift = P(oposicion | mecanismo) / P(oposicion)
#       > 1 -> la combinacion ocurre MAS de lo esperado
#       < 1 -> ocurre MENOS de lo esperado
# ============================================================

source("config.R")
con <- conectar_bd()

# ---- Funcion principal -------------------------------------

analisis_legal_oposicion <- function(
    con,
    purpose_id,
    opposition_group_id,
    min_mechanism_projects = 4,
    min_events = 20
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

  # 2. Tipos de oposicion con suficientes eventos
  sql_opp <- sprintf("
    SELECT
        et.id,
        et.name,
        COUNT(ev.id) AS n_events
    FROM event_eventtype et
    JOIN event_event ev ON ev.event_type_id = et.id
    WHERE et.event_group_id = %d
    GROUP BY et.id, et.name
    HAVING COUNT(ev.id) >= %d
    ORDER BY n_events DESC
  ", opposition_group_id, min_events)

  oposiciones <- consulta(con, sql_opp)

  # 3. Total de proyectos con al menos un evento (universo)
  sql_total <- "
    SELECT COUNT(DISTINCT m.project_id) AS total
    FROM source_mention m
    JOIN event_event ev ON ev.mention_id = m.id
  "
  total_projects <- consulta(con, sql_total)$total

  # 4. Pares (proyecto, mecanismo) para el proposito dado
  sql_mech_pairs <- sprintf("
    SELECT DISTINCT
        m.project_id,
        ev.event_type_id AS mech_type_id
    FROM event_event ev
    JOIN source_mention m      ON ev.mention_id = m.id
    JOIN event_eventtype et    ON ev.event_type_id = et.id
    WHERE et.event_group_id = 3
      AND ev.purpose_id = %d
  ", purpose_id)

  mech_pairs <- consulta(con, sql_mech_pairs)

  # 5. Pares (proyecto, tipo de oposicion)
  sql_opp_pairs <- sprintf("
    SELECT DISTINCT
        m.project_id,
        ev.event_type_id AS opp_type_id
    FROM event_event ev
    JOIN source_mention m   ON ev.mention_id = m.id
    JOIN event_eventtype et ON ev.event_type_id = et.id
    WHERE et.event_group_id = %d
  ", opposition_group_id)

  opp_pairs <- consulta(con, sql_opp_pairs)

  # ---- Calculo de co-ocurrencia ----------------------------

  # Merge: proyectos con mecanismo Y oposicion
  cooc <- mech_pairs |>
    inner_join(opp_pairs, by = "project_id") |>
    filter(
      mech_type_id %in% mecanismos$id,
      opp_type_id %in% oposiciones$id
    ) |>
    group_by(mech_type_id, opp_type_id) |>
    summarise(n_projects = n_distinct(project_id),
              .groups = "drop")

  # Mapear nombres
  cooc <- cooc |>
    left_join(mecanismos |> select(id, name),
              by = c("mech_type_id" = "id")) |>
    rename(mecanismo = name) |>
    left_join(oposiciones |> select(id, name),
              by = c("opp_type_id" = "id")) |>
    rename(oposicion = name)

  # Pivot: filas = mecanismo, columnas = oposicion
  df_crudo <- cooc |>
    select(mecanismo, oposicion, n_projects) |>
    pivot_wider(
      names_from = oposicion,
      values_from = n_projects,
      values_fill = 0
    )

  # ---- Calculo de lift -------------------------------------

  # P(oposicion) = proyectos con esa oposicion / total
  baseline_opp <- opp_pairs |>
    filter(opp_type_id %in% oposiciones$id) |>
    group_by(opp_type_id) |>
    summarise(n = n_distinct(project_id), .groups = "drop") |>
    left_join(oposiciones |> select(id, name),
              by = c("opp_type_id" = "id")) |>
    select(name, p_base = n) |>
    mutate(p_base = p_base / total_projects) |>
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
  opp_cols <- setdiff(names(df_crudo), "mecanismo")
  df_lift <- df_crudo
  for (col in opp_cols) {
    n_mech <- proj_por_mech[df_lift$mecanismo]
    p_given_mech <- df_lift[[col]] / n_mech
    p_base <- baseline_opp[col]
    df_lift[[col]] <- round(
      ifelse(p_base > 0, p_given_mech / p_base, 0),
      2
    )
  }

  list(
    crudo      = df_crudo,
    lift       = df_lift,
    mecanismos = mecanismos,
    oposiciones = oposiciones
  )
}

# ============================================================
# 1. Despojo x Violencias
# ============================================================
cat("\n=== Despojo x Violencias ===\n")
despojo <- analisis_legal_oposicion(
  con,
  purpose_id = 1,
  opposition_group_id = 1,
  min_mechanism_projects = 4
)
cat("\nConteo bruto:\n")
print(despojo$crudo)
cat("\nLift:\n")
print(despojo$lift)

# ============================================================
# 2. Defensa x Acciones colectivas
# ============================================================
cat("\n=== Defensa x Acciones colectivas ===\n")
defensa <- analisis_legal_oposicion(
  con,
  purpose_id = 2,
  opposition_group_id = 2,
  min_mechanism_projects = 4
)
cat("\nConteo bruto:\n")
print(defensa$crudo)
cat("\nLift:\n")
print(defensa$lift)

dbDisconnect(con)
