# Eventos

Un **evento** es un hecho narrado en una nota que afecta al proyecto
o a sus actores. Hay tres grandes familias de eventos, organizadas
en `event_eventgroup`:

| `event_eventgroup.id` | Nombre | Qué registra |
|-----------------------|--------|--------------|
| 1 | Violencias | Agresiones, amenazas, asesinatos, detenciones contra opositores |
| 2 | Acciones colectivas | Protestas, bloqueos, marchas, asambleas contra el proyecto |
| 3 | Mecanismos legales | Normas, recursos, procesos judiciales (despojo o defensa) |

Los mecanismos legales (grupo 3) se subdividen por propósito en
`event_event.purpose_id`:

| `event_purpose.id` | Nombre |
|--------------------|--------|
| 1 | Despojo |
| 2 | Defensa |

`purpose_id` es `NULL` para los grupos 1 y 2.

## Tablas

### `event_event`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `mention_id` | integer → `source_mention.id` | Nota × proyecto donde se reportó |
| `event_type_id` | integer → `event_eventtype.id` | Tipo de evento |
| `purpose_id` | integer → `event_purpose.id` | Solo para grupo 3 (mecanismos legales) |
| `date` | date | Fecha del hecho (puede ser NULL) |
| `number_women` | integer | Mujeres víctimas / participantes |
| `number_men` | integer | Hombres |
| `number_mix` | integer | Conteo mixto o no desagregado |
| `description` | text | Descripción libre |

### `event_involved`

Relación directa entre **participante** y **evento**: quiénes
intervinieron en el evento y en qué rol.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `event_id` | integer → `event_event.id` | Evento |
| `participant_id` | integer → `actor_participant.id` | Participante |
| `involved_role_id` | integer → `event_involvedrole.id` | Rol (víctima, promovente, etc.) |
| `number_women` | integer | |
| `number_men` | integer | |
| `number_mix` | integer | |

## Catálogos del dominio de eventos

### Grupo → tipo (dos niveles)

- `event_eventgroup`: los tres grupos mayores descritos arriba.
- `event_eventtype`: tipos concretos dentro de cada grupo
  (ej. "amenaza de muerte" en violencias, "bloqueo de carretera" en
  acciones colectivas, "amparo" en defensa legal).
  - FK `event_group_id` → `event_eventgroup.id`.
  - Campos útiles: `has_displacement` (bool, si el tipo puede
    generar desplazamiento), `purpose_defense`, `purpose_spoliation`
    (textos descriptivos cuando aplica).

### Propósito (solo grupo 3)

- `event_purpose`: 2 valores fijos (ver tabla arriba).

### Rol del involucrado

- `event_involvedrole`: catálogo plano. Cada involucrado puede tener
  un rol (víctima directa, promovente, beneficiario, etc.).

## Ubicación del evento

- **Directa**: `space_time_location` con `event_id = <id_evento>`.
- **Heredada del proyecto** (cuando no hay ubicación propia): seguir
  `event_event → source_mention → project_project →
  space_time_location`. Ver `space_time.md` para el patrón completo.

## Ejemplos

### Mecanismos legales de defensa por estado del proyecto asociado

```sql
SELECT
    st.name        AS entidad,
    COUNT(DISTINCT ev.id) AS n_defensas
FROM event_event ev
JOIN event_eventtype et ON et.id = ev.event_type_id
JOIN source_mention  m  ON m.id = ev.mention_id
JOIN space_time_location lo ON lo.project_id = m.project_id
JOIN space_time_state   st  ON st.id = lo.state_id
WHERE et.event_group_id = 3
  AND ev.purpose_id = 2           -- defensa
GROUP BY st.name
ORDER BY n_defensas DESC
```

### Violencias con número de víctimas totales

```sql
SELECT
    ev.date,
    et.name AS tipo_violencia,
    COALESCE(ev.number_women, 0)
      + COALESCE(ev.number_men, 0)
      + COALESCE(ev.number_mix, 0)  AS victimas
FROM event_event ev
JOIN event_eventtype et ON et.id = ev.event_type_id
WHERE et.event_group_id = 1
ORDER BY ev.date DESC NULLS LAST
```

### Actores que participaron en eventos (relación directa)

```sql
SELECT
    a.name,
    et.name AS tipo_evento,
    r.name  AS rol
FROM actor_actor a
JOIN actor_participant p  ON p.actor_id = a.id
JOIN event_involved    i  ON i.participant_id = p.id
JOIN event_event      ev  ON ev.id = i.event_id
JOIN event_eventtype  et  ON et.id = ev.event_type_id
LEFT JOIN event_involvedrole r ON r.id = i.involved_role_id
```

## Trampas frecuentes

- Cuando la usuaria dice "violencias", "acciones colectivas" o
  "mecanismos legales" se refiere a un **grupo** de evento
  (`event_eventgroup`), no a un tipo específico. Filtrar con
  `et.event_group_id = N`.
- En mecanismos legales (grupo 3), no olvidar `purpose_id` si la
  pregunta distingue despojo y defensa.
- `ev.date` puede ser `NULL` si la nota no precisa fecha. Para series
  de tiempo, considerar usar `source_note.date` como alternativa.
- **Directo vs indirecto** al cruzar con actores: `event_involved`
  es la participación estricta; `source_mention` da co-ocurrencia
  (actor mencionado en la misma nota que el evento, sin necesidad
  de que haya participado).
