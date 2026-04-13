# ============================================================
# Actores involucrados en mecanismos legales (event_group = 3)
# ============================================================
# Genera tres dataframes:
#   - df_event_types : conteo de proyectos por tipo de
#                      mecanismo legal (total, despojo, defensa)
#   - df_actors      : actores con sus mecanismos y conteos,
#                      enriquecidos con totales del tipo de evento
#   - df_grouped     : un renglón por actor con sus mecanismos
#                      concatenados
# ------------------------------------------------------------
# NOTA sobre el tipo de relación Actor↔Evento usada aquí:
# Este script relaciona actores y eventos de forma INDIRECTA,
# vía co-ocurrencia en la misma mención (source_mention). Es
# decir: un actor "cuenta" para un tipo de mecanismo si aparece
# en la misma nota donde se reportó ese mecanismo, aunque no
# haya sido parte formal del evento.
#
# Esta elección es POR DISEÑO, no por descuido: la pregunta de
# investigación aquí es "¿qué actores aparecen asociados
# editorialmente a mecanismos de despojo o defensa en los
# proyectos?", lo cual encaja con la co-ocurrencia.
#
# La alternativa es la relación DIRECTA vía event_involved
# (actor que participó estrictamente en el evento). Si se
# quiere esa lectura, el JOIN es:
#   actor_actor → actor_participant → event_involved →
#     event_event
# Ver references/event.md para el patrón directo.
# ============================================================

source("config.R")
con <- conectar_bd()

# ---- 1. Proyectos por tipo de mecanismo legal --------------

sql_event_types <- "
SELECT
    et.id,
    et.name,
    COUNT(DISTINCT m.project_id)
        AS project_count,
    COUNT(DISTINCT m.project_id)
        FILTER (WHERE ev.purpose_id = 1)
        AS despojo_count,
    COUNT(DISTINCT m.project_id)
        FILTER (WHERE ev.purpose_id = 2)
        AS defensa_count
FROM event_eventtype et
JOIN event_event ev    ON ev.event_type_id = et.id
JOIN source_mention m  ON ev.mention_id = m.id
WHERE et.event_group_id = 3
GROUP BY et.id, et.name
ORDER BY project_count DESC
"

df_event_types <- consulta(con, sql_event_types)

# ---- 2. Actores con sus tipos de mecanismo -----------------

sql_actors <- "
SELECT
    a.id,
    a.name,
    a.alternative_names,
    et.name AS event_type,
    COUNT(DISTINCT m.project_id)
        AS project_count,
    COUNT(DISTINCT m.project_id)
        FILTER (WHERE ev.purpose_id = 1)
        AS despojo_count,
    COUNT(DISTINCT m.project_id)
        FILTER (WHERE ev.purpose_id = 2)
        AS defensa_count
FROM actor_actor a
JOIN actor_participant p  ON p.actor_id = a.id
JOIN source_mention m     ON p.mention_id = m.id
JOIN event_event ev       ON ev.mention_id = m.id
JOIN event_eventtype et   ON ev.event_type_id = et.id
WHERE et.event_group_id = 3
GROUP BY a.id, a.name, a.alternative_names, et.name
ORDER BY project_count DESC
"

df_actors <- consulta(con, sql_actors)

# ---- 3. Enriquecer actores con totales globales ------------

df_actors_full <- df_actors |>
  left_join(
    df_event_types |>
      rename(
        total_projects = project_count,
        total_despojo  = despojo_count,
        total_defensa  = defensa_count
      ),
    by = c("event_type" = "name"),
    suffix = c("", "_et")
  ) |>
  select(-id_et)

# ---- 4. Agrupar: un renglón por actor ---------------------

df_grouped <- df_actors |>
  group_by(id, name, alternative_names) |>
  summarise(
    event_types    = paste(sort(unique(event_type)),
                           collapse = ", "),
    project_count  = sum(project_count),
    despojo_count  = sum(despojo_count),
    defensa_count  = sum(defensa_count),
    .groups = "drop"
  ) |>
  arrange(desc(project_count))

# ---- Resumen -----------------------------------------------

cat("\n=== Tipos de mecanismo legal ===\n")
print(df_event_types)

cat("\n=== Actores agrupados (primeros 20) ===\n")
print(df_grouped, n = 20)

dbDisconnect(con)
