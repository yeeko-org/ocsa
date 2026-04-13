# ============================================================
# Mecanismos legales cruzados con tipo de extractivismo
# ============================================================
# Genera tres dataframes:
#   - df_extractivism  : total de proyectos por tipo de
#                        extractivismo
#   - df_events_extr   : pivot de EventType x ExtractivismType
#                        con conteos (total, despojo, defensa)
#   - df_purpose_extr  : pivot de Propósito x ExtractivismType
# ============================================================

source("config.R")
con <- conectar_bd()

# ---- 1. Proyectos por tipo de extractivismo ----------------

sql_extractivism <- "
SELECT
    ext.id,
    ext.name,
    COUNT(DISTINCT p.id) AS total_projects
FROM project_extractivismtype ext
JOIN project_megaprojecttype_extractivism_types me
    ON me.extractivismtype_id = ext.id
JOIN project_project p
    ON p.megaproject_type_id = me.megaprojecttype_id
GROUP BY ext.id, ext.name
ORDER BY total_projects DESC
"

df_extractivism <- consulta(con, sql_extractivism)

# ---- 2. Mecanismos legales x extractivismo -----------------

sql_events_extr <- "
SELECT
    et.id,
    et.name,
    LEFT(ext.name, 25) AS extractivism_type,
    COUNT(DISTINCT p.id)
        AS project_count,
    COUNT(DISTINCT p.id)
        FILTER (WHERE ev.purpose_id = 1)
        AS despojo_count,
    COUNT(DISTINCT p.id)
        FILTER (WHERE ev.purpose_id = 2)
        AS defensa_count
FROM event_eventtype et
JOIN event_event ev    ON ev.event_type_id = et.id
JOIN source_mention m  ON ev.mention_id = m.id
JOIN project_project p ON m.project_id = p.id
JOIN project_megaprojecttype_extractivism_types me
    ON me.megaprojecttype_id = p.megaproject_type_id
JOIN project_extractivismtype ext
    ON ext.id = me.extractivismtype_id
WHERE et.event_group_id = 3
GROUP BY et.id, et.name, ext.name
ORDER BY et.name, project_count DESC
"

df_events_extr_raw <- consulta(con, sql_events_extr)

# Pivot: una columna por cada combinación métrica-extractivismo
df_events_extr <- df_events_extr_raw |>
  pivot_longer(
    cols = c(project_count, despojo_count, defensa_count),
    names_to = "metrica",
    values_to = "valor"
  ) |>
  unite("columna", metrica, extractivism_type, sep = " | ") |>
  pivot_wider(
    id_cols = name,
    names_from = columna,
    values_from = valor,
    values_fill = 0
  )

# ---- 3. Propósito x extractivismo con totales -------------

sql_purpose_extr <- "
SELECT
    pu.name AS purpose_name,
    ext.name AS extractivism_type,
    COUNT(DISTINCT p.id) AS project_count
FROM event_event ev
JOIN event_eventtype et ON ev.event_type_id = et.id
JOIN event_purpose pu   ON ev.purpose_id = pu.id
JOIN source_mention m   ON ev.mention_id = m.id
JOIN project_project p  ON m.project_id = p.id
JOIN project_megaprojecttype_extractivism_types me
    ON me.megaprojecttype_id = p.megaproject_type_id
JOIN project_extractivismtype ext
    ON ext.id = me.extractivismtype_id
WHERE et.event_group_id = 3
  AND ev.purpose_id IS NOT NULL
GROUP BY pu.name, ext.name
ORDER BY pu.name, project_count DESC
"

df_purpose_extr <- consulta(con, sql_purpose_extr) |>
  pivot_wider(
    id_cols = extractivism_type,
    names_from = purpose_name,
    values_from = project_count,
    values_fill = 0
  ) |>
  left_join(
    df_extractivism |> select(name, total_projects),
    by = c("extractivism_type" = "name")
  ) |>
  arrange(desc(total_projects))

# ---- Resumen -----------------------------------------------

cat("\n=== Proyectos por tipo de extractivismo ===\n")
print(df_extractivism)

cat("\n=== Mecanismos legales x extractivismo ===\n")
print(df_events_extr)

cat("\n=== Propósito x extractivismo ===\n")
print(df_purpose_extr)

dbDisconnect(con)
