# Esquema de la base de datos — OCSA

Índice de referencia para generar consultas en R contra la base
PostgreSQL del Observatorio de Conflictos Socioambientales. Usa este
archivo como punto de partida y carga el archivo específico de
`references/` que corresponda a tu consulta.

## Contexto del proyecto

La base registra conflictos socioambientales en México asociados a
megaproyectos extractivos (minas, presas, gasoductos, parques eólicos,
etcétera), documentados a partir de notas periodísticas (La Jornada,
Reforma, Proceso) desde 2017.

## Cómo ejecutar queries

Cada script de R usa `config.R` para conectarse. El patrón es:

```r
source("config.R")
con <- conectar_bd()

sql <- "SELECT ... FROM ..."
resultado <- consulta(con, sql)

dbDisconnect(con)
```

`consulta()` ejecuta SQL y devuelve un `tibble` (tabla de tidyverse).
El post-procesamiento (pivots, joins, cálculos) se hace con tidyverse.

## Mapa de entidades

```
                          +--------------+
                          | source_note  |
                          +------+-------+
                                 |
                        source_mention   ← HUB
                     /     |        \
      actor_participant    |    event_event
            |              |         |
        actor_actor        |     event_involved (Actor↔Evento directo)
            |              |
     (catálogos classify)  |
                           v
                      impact_impact
                           |
                   (catálogos impact)

                    project_project
                           ^
                           | (project_id en source_mention)
                           |
                 space_time_location
                 (también event_id, impact_id)
```

`source_mention` es el nodo central: toda nota se amarra a un proyecto
vía una mención, y desde ahí cuelgan eventos, afectaciones, actores y
desplazamientos.

## Dónde buscar cada cosa

| Busco información sobre… | Archivo |
|--------------------------|---------|
| Actores, participantes, intereses, membresías | `references/actor.md` |
| Megaproyectos, conflictos, tipos de extractivismo | `references/project.md` |
| Eventos (violencias, acciones colectivas, mecanismos legales) | `references/event.md` |
| Afectaciones sociales y ecológicas | `references/impact.md` |
| Desplazamiento forzado | `references/df.md` |
| Ubicaciones geográficas (estado, municipio, localidad) | `references/space_time.md` |
| Catálogos transversales (sector, país, grupo indígena, posición) | `references/classify.md` |
| Notas, menciones, artículos, historial de estatus | `references/source.md` |

## Caminos de JOIN más comunes

### Proyecto → ubicación principal

Cuando un proyecto tiene varias filas en `space_time_location`, la
ubicación "principal" es la de mayor `priority` en su
`status_location`. Este patrón aplica también para evento e impacto.

```sql
SELECT DISTINCT ON (p.id)
    p.id,
    p.name,
    st.name  AS entidad,
    mun.name AS municipio,
    loc.name AS localidad,
    lo.latitude,
    lo.longitude
FROM project_project p
LEFT JOIN space_time_location lo  ON lo.project_id = p.id
LEFT JOIN work_flux_statuscontrol sc
       ON sc.name = lo.status_location_id
LEFT JOIN space_time_state        st  ON st.id  = lo.state_id
LEFT JOIN space_time_municipality mun ON mun.id = lo.municipality_id
LEFT JOIN space_time_locality     loc ON loc.id = lo.locality_id
ORDER BY p.id, sc.priority DESC NULLS LAST
```

### Evento → su propia ubicación

```sql
JOIN space_time_location lo ON lo.event_id = ev.id
```

### Evento → ubicación del proyecto asociado

Útil cuando el evento no tiene ubicación propia registrada.

```sql
JOIN source_mention       m  ON m.id = ev.mention_id
JOIN space_time_location  lo ON lo.project_id = m.project_id
```

### Afectación → ubicación

Análogo a evento: `space_time_location.impact_id` para la ubicación
propia; si no existe, heredar vía `source_mention.project_id`.

### Actor ↔ Evento: relación directa

```sql
FROM actor_actor a
JOIN actor_participant p  ON p.actor_id = a.id
JOIN event_involved    i  ON i.participant_id = p.id
JOIN event_event      ev  ON ev.id = i.event_id
LEFT JOIN event_involvedrole r ON r.id = i.involved_role_id
```

### Actor ↔ Evento: relación indirecta (co-ocurrencia por nota)

El actor aparece mencionado en la misma nota donde se reportó el
evento. Útil cuando interesa la coincidencia editorial, no la
participación estricta.

```sql
FROM actor_actor a
JOIN actor_participant p  ON p.actor_id = a.id
JOIN source_mention    m  ON m.id = p.mention_id
JOIN event_event      ev  ON ev.mention_id = m.id
```

### Proyecto ↔ Tipo de extractivismo

`project_megaprojecttype` y `project_extractivismtype` se relacionan
muchos a muchos mediante `project_megaprojecttype_extractivism_types`.

```sql
FROM project_project p
JOIN project_megaprojecttype mt  ON mt.id = p.megaproject_type_id
JOIN project_megaprojecttype_extractivism_types mex
     ON mex.megaprojecttype_id = mt.id
JOIN project_extractivismtype et ON et.id = mex.extractivismtype_id
```

### Proyecto ↔ Nota (vía mención)

```sql
FROM project_project p
JOIN source_mention m ON m.project_id = p.id
JOIN source_note    n ON n.id = m.note_id
```

### Filtro "solo proyectos y notas validados/públicos"

Aplicar solo si la usuaria lo pidió. No aplicar por defecto.

**Para proyectos como modelo principal:**

```sql
JOIN work_flux_statuscontrol sc
     ON sc.name = p.status_validation_id
WHERE sc.is_public = TRUE
```

**Para cualquier otro modelo principal** (Event, Impact, Actor,
Participant, Displacement): alcanzar `source_note` por la ruta más
corta y filtrar su `status_register`.

```sql
JOIN source_mention m ON m.id = <modelo>.mention_id
JOIN source_note    n ON n.id = m.note_id
JOIN work_flux_statuscontrol sc
     ON sc.name = n.status_register_id
WHERE sc.is_public = TRUE
```

Notas:

- `work_flux_statuscontrol` usa el campo `name` (texto) como clave
  primaria, no un `id` numérico. Por eso el `JOIN` se hace contra
  `sc.name`.
- El mismo patrón sirve para filtrar por cualquier otro atributo del
  estatus (`priority`, `group`, etcétera).

## Convenciones de catálogos

Muchos catálogos del sistema se organizan en jerarquías de **grupo →
tipo → subtipo**. No todos los catálogos tienen los tres niveles: el
mínimo es una tabla plana de valores, el intermedio agrupa tipos en
grupos, y el máximo permite subtipos dentro de los tipos.

| Entidad | Grupo | Tipo | Subtipo |
|--------|-------|------|---------|
| Eventos | `event_eventgroup` | `event_eventtype` | — |
| Afectaciones | `impact_impactgroup` | `impact_impacttype` | `impact_impactsubtype` |
| Proyectos (extractivismo) | — | `project_extractivismtype` | `project_megaprojecttype` |
| Participación | `classify_participantgroup` | `classify_participanttype` | — |
| Sectores (de actores) | `classify_sectorgroup` | `classify_sector` | — |
| Intereses | `classify_interestgroup` | `classify_interesttype` | `classify_interestsubtype` |

Catálogos planos, sin jerarquía: `project_statusproject`,
`project_conflict`, `classify_country`, `classify_indigenousgroup`,
`classify_belong`, `event_purpose`, `event_involvedrole`,
`df_dimension`, `df_populationsize`, `df_temporality`, `source_source`,
`source_discardedreason`.

### Sobre el filtro de validación en catálogos

Casi todos los catálogos tienen un campo `status_validation` (FK a
`work_flux_statuscontrol`) que permite distinguir valores activos y
en revisión. **Por defecto no se filtra** por este campo al consultar
catálogos, porque suele restar datos y confundir el análisis. Está
documentado en cada `references/<app>.md` para cuando haga falta
aplicarlo.
