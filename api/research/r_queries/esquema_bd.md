# Esquema de la base de datos — OCSA

Referencia completa para generar consultas en R contra la base
de datos PostgreSQL del Observatorio de Conflictos
Socioambientales (OCSA). Pega este documento como contexto
cuando le pidas a un asistente de IA que te genere queries.

## Contexto del proyecto

La base registra conflictos socioambientales en Mexico
asociados a megaproyectos extractivos (minas, presas,
gasoductos, parques eolicos, etc.), documentados a partir de
notas periodisticas (La Jornada, Reforma, Proceso) desde 2017.

## Como ejecutar queries

Cada script de R usa `config.R` para conectarse. El patron es:

```r
source("config.R")
con <- conectar_bd()

resultado <- consulta(con, "SELECT ... FROM ...")

dbDisconnect(con)
```

La funcion `consulta()` ejecuta SQL y devuelve un tibble
(tabla de tidyverse). El post-procesamiento (pivots, joins,
calculos) se hace con tidyverse.

---

## Entidades principales

### Mencion (hub central)

Todo pasa por `source_mention`: conecta una nota periodistica
con un proyecto, y a partir de ahi se registran participantes,
eventos y afectaciones.

| Tabla | Columnas clave |
|-------|---------------|
| `source_note` | `id`, `title`, `date`, `url`, `source_page_id` |
| `source_mention` | `id`, `note_id`, `project_id` |

### Proyecto (Megaproyecto)

Obra fisica de gran escala. Puede tener un proyecto padre.

| Tabla | Columnas clave |
|-------|---------------|
| `project_project` | `id`, `name`, `parent_project_id`, `conflict_id`, `megaproject_type_id`, `status_project_id`, `is_grouper` |
| `project_conflict` | `id`, `name` |
| `project_megaprojecttype` | `id`, `name`, `description` |
| `project_extractivismtype` | `id`, `name` |
| `project_megaprojecttype_extractivism_types` | `megaprojecttype_id`, `extractivismtype_id` (tabla M2M) |
| `project_statusproject` | `id`, `name` |

Tipos de extractivismo: agro, mineria, hidricos, energia,
urbano, infraestructura. Un `megaproject_type` puede pertenecer
a varios tipos de extractivismo (relacion muchos a muchos).

Estatus del proyecto: planeacion, construccion, activo,
ampliacion, suspension, cancelado, clausurado.

### Actor / Participante

Persona, comunidad u organizacion vinculada a un proyecto.

| Tabla | Columnas clave |
|-------|---------------|
| `actor_actor` | `id`, `name`, `alternative_names`, `sector_id`, `indigenous_group_id`, `parent_actor_id` |
| `actor_participant` | `id`, `actor_id`, `mention_id` |
| `actor_participant_participant_types` | `participant_id`, `participanttype_id` (tabla M2M) |

Catalogos de posicion del participante (`classify_participantgroup`):

| id | nombre | Significado |
|----|--------|-------------|
| 1 | oppose | Se opone al proyecto |
| 2 | neutral | Media entre partes |
| 3 | support | Apoya o ejecuta el proyecto |

Catalogos de sector (`classify_sectorgroup` / `classify_sector`):
Ej. "Institucion federal", "Empresa privada", "Ciudadania
organizada".

### Evento

Hecho narrado en una nota que afecta al proyecto o sus actores.

| Tabla | Columnas clave |
|-------|---------------|
| `event_event` | `id`, `mention_id`, `event_type_id`, `purpose_id`, `description`, `date` |
| `event_eventtype` | `id`, `name`, `event_group_id`, `has_displacement` |
| `event_eventgroup` | `id`, `name` |
| `event_purpose` | `id`, `name` |
| `event_involved` | `id`, `event_id`, `participant_id`, `involved_role_id` |
| `event_involvedrole` | `id`, `name` |

Los 4 grupos de evento:

| Grupo | event_group_id | purpose_id | Descripcion |
|-------|---------------|------------|-------------|
| Violencias | 1 | — | Acciones contra opositores: amenazas, agresiones, asesinatos |
| Acciones colectivas | 2 | — | Movilizaciones contra el proyecto: protestas, bloqueos |
| Mecanismos legales (despojo) | 3 | 1 | Normativas que facilitan el despojo |
| Mecanismos legales (defensa) | 3 | 2 | Recursos juridicos en defensa de comunidades |

**Importante:** Los mecanismos legales comparten `event_group_id = 3`
y se distinguen por `purpose_id` (1 = despojo, 2 = defensa).
`purpose_id` es NULL para los otros grupos.

### Afectacion (Impact)

Consecuencia negativa directa del megaproyecto.

| Tabla | Columnas clave |
|-------|---------------|
| `impact_impact` | `id`, `mention_id`, `impact_type_id`, `impact_subtype_id`, `description`, `is_potential` |
| `impact_impacttype` | `id`, `name`, `impact_group_id`, `status_validation_id`, `has_displacement` |
| `impact_impactgroup` | `id`, `name` |
| `impact_impactsubtype` | `id`, `name`, `impact_type_id` |

Grupos de afectacion:

| id | nombre | Ejemplos |
|----|--------|----------|
| 1 | Social | Desplazamiento, salud publica, derechos humanos |
| 2 | Ecologico | Contaminacion, deforestacion, biodiversidad |

**Nota:** Solo usar `impact_impacttype` donde
`status_validation_id = 'validated'` (los demas estan en
revision).

### Desplazamiento forzado

Registro detallado de desplazamiento de personas asociado a un
impacto o evento.

| Tabla | Columnas clave |
|-------|---------------|
| `df_displacement` | `id`, `impact_id`, `event_id`, `dimension_id`, `population_size_id`, `temporality_id` |
| `df_dimension` | Interno / Internacional |
| `df_populationsize` | Individuos-Familias / Masivo |
| `df_temporality` | Permanente / Temporal |

### Ubicaciones geograficas

| Tabla | Columnas clave |
|-------|---------------|
| `space_time_state` | `id`, `name` (estado de Mexico) |
| `space_time_municipality` | `id`, `name`, `state_id` |
| `space_time_locality` | `id`, `name`, `municipality_id`, `latitude`, `longitude` |

---

## Caminos de JOIN mas comunes

Estos son los caminos para conectar entidades a traves de la
base de datos. Cada flecha indica un JOIN por la columna
especificada.

### De Proyecto a Evento
```
project_project
  <- source_mention.project_id
  <- event_event.mention_id
  -> event_eventtype.id = event_event.event_type_id
```

### De Proyecto a Afectacion
```
project_project
  <- source_mention.project_id
  <- impact_impact.mention_id
  -> impact_impacttype.id = impact_impact.impact_type_id
  -> impact_impactgroup.id = impact_impacttype.impact_group_id
```

### De Proyecto a Actor
```
project_project
  <- source_mention.project_id
  <- actor_participant.mention_id
  -> actor_actor.id = actor_participant.actor_id
```

### De Actor a Evento (a traves del involucramiento)
```
actor_actor
  <- actor_participant.actor_id
  <- event_involved.participant_id
  -> event_event.id = event_involved.event_id
```

### De Actor a Evento (co-ocurrencia en la misma mencion)
```
actor_actor
  <- actor_participant.actor_id
  -> source_mention.id = actor_participant.mention_id
  <- event_event.mention_id
```

### De Proyecto a Tipo de extractivismo
```
project_project
  -> project_megaprojecttype.id = project_project.megaproject_type_id
  <- project_megaprojecttype_extractivism_types.megaprojecttype_id
  -> project_extractivismtype.id = ...extractivismtype_id
```

### De Evento a Ubicacion del proyecto
```
event_event
  -> source_mention.id = event_event.mention_id
  -> project_project.id = source_mention.project_id
  <- space_time_locality (a traves de la relacion de ubicaciones del proyecto)
```

---

## Ejemplo completo de query en R

Contar proyectos por tipo de evento, distinguiendo despojo y
defensa en mecanismos legales:

```r
source("config.R")
con <- conectar_bd()

sql <- "
SELECT
    eg.name AS grupo_evento,
    et.name AS tipo_evento,
    pu.name AS proposito,
    COUNT(DISTINCT m.project_id) AS n_proyectos
FROM event_event ev
JOIN event_eventtype et   ON ev.event_type_id = et.id
JOIN event_eventgroup eg  ON et.event_group_id = eg.id
LEFT JOIN event_purpose pu ON ev.purpose_id = pu.id
JOIN source_mention m     ON ev.mention_id = m.id
GROUP BY eg.name, et.name, pu.name
ORDER BY eg.name, n_proyectos DESC
"

df_resultado <- consulta(con, sql)
print(df_resultado)

dbDisconnect(con)
```
