# Megaproyectos y conflictos

Un **proyecto** es una obra física concreta (mina, presa, parque
eólico, gasoducto, urbanización, etcétera). Un **conflicto** es una
agrupación temática que junta varios proyectos relacionados.

## Tablas

### `project_project`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `name` | text | Nombre del proyecto |
| `alternative_name` | text | Otros nombres conocidos |
| `description` | text | |
| `parent_project_id` | integer → `project_project.id` | Proyecto agrupador |
| `conflict_id` | integer → `project_conflict.id` | Conflicto temático al que pertenece |
| `megaproject_type_id` | integer → `project_megaprojecttype.id` | Tipo de megaproyecto |
| `status_project_id` | text → `project_statusproject.name` | Etapa actual del proyecto |
| `is_grouper` | bool | Si es un "proyecto paraguas" que agrupa a otros |
| `status_validation_id` | text → `work_flux_statuscontrol.name` | Estatus editorial/validación |
| `status_location_id` | text → `work_flux_statuscontrol.name` | Estatus de validación de la ubicación |

**M2M salientes:**

- `project_project_editors` (`project_id`, `user_id`): editores
  asignados.
- `project_project_others_parents` (`from_project_id`, `to_project_id`):
  proyectos padres adicionales.

### `project_conflict`

Catálogo de conflictos temáticos.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `description` | text |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

### `project_projectfile`

Archivos asociados al proyecto (PDFs, imágenes).

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `project_id` | integer → `project_project.id` |
| `file` | text (ruta) |
| `uploaded_at` | timestamp |

## Catálogos de clasificación del proyecto

### Tipo de extractivismo → tipo de megaproyecto (dos niveles)

- `project_extractivismtype`: 6 valores fijos.
  `agro`, `mineria`, `hidricos`, `energia`, `urbano`, `infra`.
- `project_megaprojecttype`: tipos concretos de megaproyecto
  (mina a cielo abierto, presa hidroeléctrica, parque eólico, etc.).
- Relación muchos a muchos mediante
  `project_megaprojecttype_extractivism_types` (columnas
  `megaprojecttype_id`, `extractivismtype_id`): un tipo de
  megaproyecto puede mapear a varios extractivismos.

### Etapa del proyecto

- `project_statusproject`: catálogo plano. Valores típicos:
  `planeación`, `construcción`, `activo`, `ampliación`, `suspensión`,
  `cancelado`, `clausurado`.
- Nota: `project_statusproject` usa `name` (texto) como PK; por eso
  el JOIN es `... ON p.status_project_id = sp.name`.

## Ejemplo: proyectos activos por tipo de extractivismo

```sql
SELECT
    et.name AS extractivismo,
    COUNT(DISTINCT p.id) AS n_proyectos
FROM project_project p
JOIN project_megaprojecttype mt  ON mt.id = p.megaproject_type_id
JOIN project_megaprojecttype_extractivism_types mex
                                 ON mex.megaprojecttype_id = mt.id
JOIN project_extractivismtype et ON et.id = mex.extractivismtype_id
JOIN project_statusproject sp    ON sp.name = p.status_project_id
WHERE sp.name = 'activo'
GROUP BY et.name
ORDER BY n_proyectos DESC
```

## Ubicación del proyecto

Un proyecto puede tener varias ubicaciones registradas en
`space_time_location` (con `project_id` como FK). La ubicación
"principal" es la de mayor `priority` de su `status_location`. Ver
`space_time.md` para el patrón completo con `Subquery` /
`DISTINCT ON`.

## Trampas frecuentes

- Un proyecto puede ser **agrupador** (`is_grouper = TRUE`) y no
  corresponder a una obra concreta, sino a un paraguas. Filtrarlos o
  considerarlos según el análisis.
- `conflict_id` puede ser `NULL`. No todos los proyectos están
  incluidos en un conflicto temático.
- El campo `status_validation` del proyecto se aplica para filtrar
  "proyectos validados/públicos". Ver `esquema_bd.md` §"Filtro solo
  validados/públicos".
