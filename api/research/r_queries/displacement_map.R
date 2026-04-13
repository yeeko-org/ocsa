# ============================================================
# Mapa de desplazamiento forzado por proyecto
# ============================================================
# Genera un mapa estático (ggplot2 + sf) con los proyectos
# que tienen eventos o afectaciones de desplazamiento forzado,
# posicionados según la ubicación geográfica del proyecto.
#
# Cada punto muestra:
#   - Nombre del proyecto
#   - Número de eventos de desplazamiento
#   - Número de afectaciones de desplazamiento
#
# Paquetes requeridos (instalar solo la primera vez):
#   install.packages(c("sf", "rnaturalearth",
#                      "rnaturalearthdata", "ggrepel"))
# ============================================================

source("config.R")
library(sf)
library(ggrepel)

con <- conectar_bd()

# ============================================================
# PASO 0 — Descubrir la tabla que liga proyectos a localidades
# ============================================================
# El esquema no documenta explícitamente la tabla M2M.
# Esta sección busca automáticamente tablas que referencien
# tanto project_project como space_time_locality.
#
# Si ya sabes el nombre de la tabla, puedes comentar este
# bloque y asignar directamente:
#   GEO_LINK_TABLE <- "nombre_de_la_tabla"

cat("Buscando tabla de enlace proyecto-localidad...\n")

sql_discover <- "
SELECT DISTINCT tc.table_name
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
    AND tc.table_schema = ccu.table_schema
WHERE tc.table_schema = 'ocsa'
  AND tc.constraint_type = 'FOREIGN KEY'
  AND ccu.table_name IN ('project_project', 'space_time_locality')
GROUP BY tc.table_name
HAVING COUNT(DISTINCT ccu.table_name) = 2
"

geo_link_candidates <- consulta(con, sql_discover)

if (nrow(geo_link_candidates) == 0) {
  # Fallback: buscar tablas M2M por convención de nombres Django
  sql_fallback <- "
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema = 'ocsa'
    AND (
      table_name LIKE 'project_project_locali%'
      OR table_name LIKE 'project_project_space%'
      OR table_name LIKE 'space_time_project%'
      OR table_name LIKE '%project%localit%'
    )
  ORDER BY table_name
  "
  geo_link_candidates <- consulta(con, sql_fallback)
}

if (nrow(geo_link_candidates) == 0) {
  stop(paste(
    "No se encontró tabla de enlace proyecto-localidad.",
    "Revisa manualmente con:",
    "  SELECT table_name FROM information_schema.tables",
    "  WHERE table_schema = 'ocsa'",
    "  AND table_name LIKE '%local%' OR table_name LIKE '%space%';",
    sep = "\n"
  ))
}

GEO_LINK_TABLE <- geo_link_candidates$table_name[1]
cat("  -> Tabla encontrada:", GEO_LINK_TABLE, "\n")

# Descubrir nombres de columnas FK en la tabla de enlace
sql_cols <- sprintf("
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ocsa'
  AND table_name = '%s'
ORDER BY ordinal_position
", GEO_LINK_TABLE)

geo_link_cols <- consulta(con, sql_cols)$column_name

# Identificar columna que apunta a project y a locality
project_col <- geo_link_cols[grepl("project", geo_link_cols)][1]
locality_col <- geo_link_cols[grepl("localit", geo_link_cols)][1]

if (is.na(project_col) || is.na(locality_col)) {
  cat("  Columnas disponibles:", paste(geo_link_cols, collapse = ", "), "\n")
  stop("No se pudieron identificar las FK automáticamente. Ajusta project_col y locality_col manualmente.")
}

cat("  -> FK proyecto:", project_col, "\n")
cat("  -> FK localidad:", locality_col, "\n\n")


# ============================================================
# PASO 1 — Eventos de desplazamiento por proyecto + coords
# ============================================================
# event_eventtype.has_displacement = TRUE identifica eventos
# que implican desplazamiento forzado.

sql_events <- sprintf("
SELECT
    p.id                          AS project_id,
    p.name                        AS project_name,
    COUNT(DISTINCT ev.id)         AS n_displacement_events
FROM project_project p
JOIN source_mention m             ON m.project_id = p.id
JOIN event_event ev               ON ev.mention_id = m.id
JOIN event_eventtype et           ON ev.event_type_id = et.id
WHERE et.has_displacement = TRUE
GROUP BY p.id, p.name
")

df_events <- consulta(con, sql_events)

cat("Proyectos con eventos de desplazamiento:", nrow(df_events), "\n")


# ============================================================
# PASO 2 — Afectaciones de desplazamiento por proyecto
# ============================================================
# impact_impacttype.has_displacement = TRUE identifica
# afectaciones de desplazamiento.

sql_impacts <- "
SELECT
    p.id                          AS project_id,
    p.name                        AS project_name,
    COUNT(DISTINCT i.id)          AS n_displacement_impacts
FROM project_project p
JOIN source_mention m             ON m.project_id = p.id
JOIN impact_impact i              ON i.mention_id = m.id
JOIN impact_impacttype it         ON i.impact_type_id = it.id
WHERE it.has_displacement = TRUE
  AND it.status_validation_id = 'validated'
GROUP BY p.id, p.name
"

df_impacts <- consulta(con, sql_impacts)

cat("Proyectos con afectaciones de desplazamiento:", nrow(df_impacts), "\n")


# ============================================================
# PASO 3 — Coordenadas de los proyectos
# ============================================================
# Toma la localidad más reciente (ID más alto) asociada al
# proyecto. Si un proyecto tiene varias localidades, se usa
# solo la última registrada.

sql_coords <- sprintf("
SELECT
    sub.project_id,
    loc.latitude                  AS lat,
    loc.longitude                 AS lon
FROM (
    SELECT
        gl.%s                     AS project_id,
        MAX(gl.%s)                AS last_locality_id
    FROM %s gl
    GROUP BY gl.%s
) sub
JOIN space_time_locality loc      ON loc.id = sub.last_locality_id
WHERE loc.latitude IS NOT NULL
  AND loc.longitude IS NOT NULL
", project_col, locality_col, GEO_LINK_TABLE, project_col)

df_coords <- consulta(con, sql_coords)

cat("Proyectos con coordenadas:", nrow(df_coords), "\n")


# ============================================================
# PASO 4 — Combinar datos
# ============================================================
# Unir eventos + afectaciones + coordenadas.
# Solo se grafican proyectos que tengan AL MENOS un evento
# o una afectación de desplazamiento Y tengan coordenadas.

df_displacement <- df_events |>
  full_join(df_impacts, by = c("project_id", "project_name")) |>
  mutate(
    n_displacement_events  = replace_na(n_displacement_events, 0),
    n_displacement_impacts = replace_na(n_displacement_impacts, 0),
    total_displacement     = n_displacement_events + n_displacement_impacts
  ) |>
  inner_join(df_coords, by = "project_id") |>
  filter(!is.na(lat), !is.na(lon))

cat("\nProyectos con desplazamiento Y coordenadas:", nrow(df_displacement), "\n")

if (nrow(df_displacement) == 0) {
  dbDisconnect(con)
  stop("No hay proyectos con desplazamiento y coordenadas. Revisa los datos.")
}


# ============================================================
# PASO 5 — Mapa estático con ggplot2 + sf
# ============================================================

# Convertir a objeto sf
sf_displacement <- st_as_sf(
  df_displacement,
  coords = c("lon", "lat"),
  crs = 4326
)

# Obtener geometría de México desde rnaturalearth
mexico <- rnaturalearth::ne_countries(
  scale = "medium",
  country = "Mexico",
  returnclass = "sf"
)

mexico_states <- rnaturalearth::ne_states(
  country = "Mexico",
  returnclass = "sf"
)

# Construir etiqueta para popups
sf_displacement <- sf_displacement |>
  mutate(
    label = paste0(
      project_name,
      "\nEv: ", n_displacement_events,
      " | Af: ", n_displacement_impacts
    )
  )

# Paleta de color según intensidad total
mapa <- ggplot() +
  # Capa base: estados de México
  geom_sf(
    data = mexico_states,
    fill = "gray95",
    color = "gray70",
    linewidth = 0.3
  ) +
  # Puntos de desplazamiento
  geom_sf(
    data = sf_displacement,
    aes(size = total_displacement, color = total_displacement),
    alpha = 0.75,
    shape = 16
  ) +
  # Etiquetas de proyecto (evitando sobreposición)
  geom_text_repel(
    data = sf_displacement,
    aes(label = project_name, geometry = geometry),
    stat = "sf_coordinates",
    size = 2.5,
    color = "gray20",
    max.overlaps = 15,
    segment.color = "gray50",
    segment.size = 0.3,
    nudge_y = 0.3,
    seed = 42
  ) +
  # Escala de color
  scale_color_gradient(
    low = "#FDAE61",
    high = "#D73027",
    name = "Total\ndesplaz."
  ) +
  scale_size_continuous(
    range = c(2, 10),
    name = "Total\ndesplaz."
  ) +
  # Límites geográficos de México
  coord_sf(
    xlim = c(-118, -86),
    ylim = c(14, 33),
    expand = FALSE
  ) +
  # Tema y títulos
  labs(
    title = "Desplazamiento forzado por proyecto",
    subtitle = "Eventos y afectaciones de desplazamiento asociados a megaproyectos",
    caption = paste(
      "Fuente: OCSA |",
      "Ev = eventos de desplazamiento |",
      "Af = afectaciones de desplazamiento |",
      "Tamaño y color = total combinado"
    )
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title    = element_text(face = "bold", size = 14),
    plot.subtitle = element_text(color = "gray40", size = 10),
    plot.caption  = element_text(color = "gray50", size = 7,
                                 hjust = 0),
    legend.position = "right",
    panel.grid = element_line(color = "gray90")
  ) +
  # Unificar leyendas de color y tamaño
  guides(
    color = guide_legend(),
    size  = guide_legend()
  )

# ---- Guardar el mapa -----------------------------------------

output_file <- "mapa_desplazamiento.png"

ggsave(
  output_file,
  plot = mapa,
  width = 14,
  height = 9,
  dpi = 300,
  bg = "white"
)

cat("\nMapa guardado en:", output_file, "\n")

# ---- Tabla resumen -------------------------------------------

cat("\n=== Resumen por proyecto ===\n")
df_displacement |>
  select(project_name, n_displacement_events,
         n_displacement_impacts, total_displacement) |>
  arrange(desc(total_displacement)) |>
  print(n = 30)

dbDisconnect(con)


