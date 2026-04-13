# Afectaciones

Una **afectación** (o impacto) es una consecuencia negativa directa
del megaproyecto sobre comunidades, territorio o ecosistemas. Se
organiza en dos grupos: sociales y ecológicos.

## Tablas

### `impact_impact`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `mention_id` | integer → `source_mention.id` | Nota × proyecto donde se reportó |
| `impact_type_id` | integer → `impact_impacttype.id` | Tipo |
| `impact_subtype_id` | integer → `impact_impactsubtype.id` | Subtipo (puede ser NULL) |
| `description` | text | Descripción libre |
| `is_potential` | bool | Si la afectación es real (FALSE) o apenas potencial/previsible (TRUE) |

## Catálogos del dominio de afectaciones

Jerarquía de tres niveles: **grupo → tipo → subtipo**.

### `impact_impactgroup`

Dos valores fijos:

| id | nombre | Ejemplos |
|----|--------|----------|
| 1 | Social | Desplazamiento, salud pública, derechos humanos, cultura |
| 2 | Ecológico | Contaminación, deforestación, pérdida de biodiversidad |

Campo útil: `is_social` (bool, `TRUE` para el grupo social).

### `impact_impacttype`

Tipos concretos dentro de cada grupo.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `short_name` | text |
| `impact_group_id` | integer → `impact_impactgroup.id` |
| `has_displacement` | bool |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

### `impact_impactsubtype`

Subtipos dentro de cada tipo. Es opcional: un impacto puede tener
solo `impact_type_id` y dejar `impact_subtype_id` en `NULL`.

| Columna | Tipo |
|---------|------|
| `id` | integer |
| `name` | text |
| `impact_type_id` | integer → `impact_impacttype.id` |
| `status_validation_id` | text → `work_flux_statuscontrol.name` |

## Ubicación de la afectación

- **Directa**: `space_time_location.impact_id = <id_afectacion>`.
- **Heredada del proyecto**: vía `source_mention.project_id`.
- Se selecciona la ubicación de mayor
  `status_location.priority` cuando hay varias (ver `space_time.md`).

## Ejemplos

### Afectaciones ecológicas por estado del proyecto

```sql
SELECT
    st.name  AS entidad,
    it.name  AS tipo_afectacion,
    COUNT(DISTINCT im.id) AS n_afectaciones
FROM impact_impact im
JOIN impact_impacttype  it ON it.id = im.impact_type_id
JOIN impact_impactgroup ig ON ig.id = it.impact_group_id
JOIN source_mention     m  ON m.id = im.mention_id
JOIN space_time_location lo ON lo.project_id = m.project_id
JOIN space_time_state   st  ON st.id = lo.state_id
WHERE ig.id = 2   -- ecológico
GROUP BY st.name, it.name
ORDER BY n_afectaciones DESC
```

### Afectaciones sociales con subtipo desglosado

```sql
SELECT
    it.name AS tipo,
    st.name AS subtipo,
    COUNT(*) AS n
FROM impact_impact im
JOIN impact_impacttype it  ON it.id = im.impact_type_id
LEFT JOIN impact_impactsubtype st ON st.id = im.impact_subtype_id
WHERE it.impact_group_id = 1  -- social
GROUP BY it.name, st.name
ORDER BY it.name, n DESC
```

## Trampas frecuentes

- `is_potential = TRUE` marca afectaciones que se proyectan o
  advierten, pero aún no ocurrieron. Si la pregunta es "afectaciones
  reales", filtrar `im.is_potential IS NOT TRUE`.
- `impact_subtype_id` es opcional. Usar `LEFT JOIN` al unir con
  `impact_impactsubtype` para no perder registros sin subtipo.
- Los catálogos `impact_impacttype` e `impact_impactsubtype` tienen
  `status_validation`. Existen tipos en revisión conviviendo con
  tipos validados; por defecto no se filtran (ver `esquema_bd.md`).
- La misma afectación puede mencionarse en varias notas (varias
  `source_mention`). Para contar "afectaciones únicas", decidir si
  cuentas por `im.id` o si agrupas por proyecto + tipo.
