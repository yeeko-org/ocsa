# Actores y participantes

Un **actor** es una persona, comunidad, organización o institución
vinculada a uno o varios proyectos. Un actor se convierte en
**participante** cuando aparece mencionado en una nota específica:
cada aparición genera una fila en `actor_participant` que liga al
actor con la mención correspondiente.

## Tablas

### `actor_actor`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `name` | text | Nombre principal |
| `std_name` | text | Nombre normalizado |
| `alternative_names` | text | Otros nombres separados por coma |
| `parent_actor_id` | integer → `actor_actor.id` | Actor agrupador (jerarquía propia) |
| `sector_id` | integer → `classify_sector.id` | Sector al que pertenece |
| `indigenous_group_id` | integer → `classify_indigenousgroup.id` | Grupo indígena (si aplica) |
| `sex` | char | Sexo cuando es persona individual |
| `geo_reach` | char | Alcance geográfico |
| `is_incomplete` | bool | Captura pendiente |
| `status_validation_id` | text → `work_flux_statuscontrol.name` | Estatus de validación |

**M2M salientes:**

- `actor_actor_countries` (columnas `actor_id`, `country_id`): países
  de origen del actor. Liga con `classify_country`.
- `actor_actor_belongs` (columnas `actor_id`, `belong_id`): etiquetas
  de pertenencia/vulnerabilidad. Liga con `classify_belong`.
- `actor_actor_others_parents` (`from_actor_id`, `to_actor_id`):
  padres adicionales distintos del `parent_actor_id` principal.

### `actor_participant`

Una fila por cada aparición de un actor en una nota (mención).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `actor_id` | integer → `actor_actor.id` | Actor referido |
| `mention_id` | integer → `source_mention.id` | Nota × proyecto donde aparece |

**M2M:** `actor_participant_participant_types` (`participant_id`,
`participanttype_id`) liga cada participación con uno o varios
**tipos de participación** (`classify_participanttype`). De ahí se
deriva la *posición* del participante (a favor / en contra / neutral)
vía `classify_participantgroup`.

### `actor_interest`

Motivos/intereses del participante en el proyecto.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `participant_id` | integer → `actor_participant.id` |
| `interest_subtype_id` | integer → `classify_interestsubtype.id` |
| `text` | text (descripción libre) |

### `actor_member`

Relación "pertenece a" entre actores (ej. una persona dirige o
pertenece a una organización). Modelo self-referencial.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `actor_individual_id` | integer → `actor_actor.id` | Miembro |
| `actor_collective_id` | integer → `actor_actor.id` | Colectivo al que pertenece |
| `membership_type` | char | `director`, `investor`, `chief_executive`, `member`, `other` |

## Catálogos del dominio de actores

Estos catálogos viven en `classify_*` y están documentados en
`classify.md`. Resumen para orientación:

- **Sector** → `classify_sector` agrupado por `classify_sectorgroup`
  (tipo con grupo, dos niveles).
- **Tipos de participación** → `classify_participanttype` agrupado por
  `classify_participantgroup` (dos niveles). La **posición** se deriva
  del `position` de `classify_participanttype` (`support`, `oppose`,
  `neutral`, etc.).
- **Pertenencias / vulnerabilidades** → `classify_belong` (catálogo
  plano).
- **Grupo indígena** → `classify_indigenousgroup` (plano).
- **Países** → `classify_country` (plano).
- **Intereses** → `classify_interestgroup` → `classify_interesttype`
  → `classify_interestsubtype` (tres niveles).

## Ejemplo: actores que se oponen a proyectos de minería

```sql
SELECT DISTINCT
    a.id,
    a.name
FROM actor_actor a
JOIN actor_participant  p   ON p.actor_id = a.id
JOIN actor_participant_participant_types pt
                              ON pt.participant_id = p.id
JOIN classify_participanttype tt
                              ON tt.id = pt.participanttype_id
JOIN source_mention     m   ON m.id = p.mention_id
JOIN project_project    pr  ON pr.id = m.project_id
JOIN project_megaprojecttype mt
                              ON mt.id = pr.megaproject_type_id
JOIN project_megaprojecttype_extractivism_types mex
                              ON mex.megaprojecttype_id = mt.id
JOIN project_extractivismtype et
                              ON et.id = mex.extractivismtype_id
WHERE tt.position = 'oppose'
  AND et.name ILIKE '%miner%'
```

## Trampas frecuentes

- Un actor puede tener varias filas en `actor_participant` (una por
  cada mención). Si se cuentan actores únicos, usar `DISTINCT` o
  `COUNT(DISTINCT a.id)`.
- Un participante puede tener **varios** tipos en
  `actor_participant_participant_types`. Si la pregunta es "¿cuántos
  actores son oposición?", hay que filtrar por tipo y luego agrupar
  por actor, porque el mismo actor puede aparecer a la vez como
  opositor en una nota y como neutral en otra.
- Los `alternative_names` son texto separado por coma (un solo campo),
  no una tabla; para buscar por nombre, cubrir `name`, `std_name` y
  `alternative_names`.
