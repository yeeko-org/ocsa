# Desplazamiento forzado

Registro detallado de casos de desplazamiento forzado de personas
asociados a un evento o a una afectación. Es una tabla hija: cada
fila de `df_displacement` cuelga de **un** `event_event` o de **una**
`impact_impact` (o de ambos, si la narrativa lo amerita).

## Tabla principal

### `df_displacement`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `event_id` | integer → `event_event.id` | Evento asociado (nullable) |
| `impact_id` | integer → `impact_impact.id` | Afectación asociada (nullable) |
| `dimension_id` | integer → `df_dimension.id` | Interno o internacional |
| `population_size_id` | integer → `df_populationsize.id` | Tamaño de la población |
| `temporality_id` | integer → `df_temporality.id` | Permanencia del desplazamiento |
| `rithm` | text | Ritmo del desplazamiento (texto libre) |
| **Origen** | | |
| `origin_state_id` | integer → `space_time_state.id` | |
| `origin_municipality_id` | integer → `space_time_municipality.id` | |
| `origin_locality_id` | integer → `space_time_locality.id` | |
| **Destino** | | |
| `destination_country_id` | integer → `classify_country.id` | Solo para desplazamiento internacional |
| `destination_state_id` | integer → `space_time_state.id` | |
| `destination_municipality_id` | integer → `space_time_municipality.id` | |
| `destination_locality_id` | integer → `space_time_locality.id` | |

## Catálogos

### `df_dimension`

Valores fijos:

| id | name | show_states | show_countries |
|----|------|-------------|----------------|
| 1 | Interno | TRUE | FALSE |
| 2 | Internacional | FALSE | TRUE |

El flag `show_countries` indica que el destino es un país (usar
`destination_country_id`); `show_states` indica que el destino es
dentro de México (usar `destination_state_id`,
`destination_municipality_id`, `destination_locality_id`).

### `df_populationsize`

| id | name |
|----|------|
| 1 | Individuos y/o familias |
| 2 | Masivo - Comunidades enteras |

### `df_temporality`

| id | name |
|----|------|
| 1 | Temporal |
| 2 | Permanente |

## Ubicación en desplazamiento: menú de opciones

El desplazamiento **no** usa `space_time_location`. Sus columnas de
origen y destino apuntan directamente a
`space_time_state` / `space_time_municipality` / `space_time_locality`
(y `classify_country` para destino internacional). Esto difiere de
cómo se resuelve la ubicación para proyectos, eventos y afectaciones.

Además, como `df_displacement` cuelga de un evento o afectación (vía
`event_id` o `impact_id`, ambos nullable), puede heredar
indirectamente la ubicación directa de esas entidades, y por la
mención de la nota también la ubicación del proyecto.

Cuando la usuaria pida "la ubicación" de un desplazamiento, **el
agente debe preguntar** cuál o cuáles niveles quiere, porque no hay
default limpio. El menú:

1. **Origen** del desplazamiento (`origin_state_id`,
   `origin_municipality_id`, `origin_locality_id` en
   `df_displacement`).
2. **Destino** del desplazamiento
   (`destination_state/municipality/locality_id` para interno;
   `destination_country_id` para internacional, según
   `df_dimension`).
3. **Ubicación directa del evento o afectación asociados**
   (`space_time_location` filtrando por `event_id` o `impact_id`).
   Relevante solo en los pocos casos en que evento o afectación
   tienen ubicación propia registrada.
4. **Ubicación del proyecto** al que pertenece la nota, vía
   `mention → project → space_time_location`, con el patrón canónico
   de `status_location.priority`.

Después de que la usuaria elija, combinar los niveles pedidos en un
solo `SELECT` con `LEFT JOIN`s (los cuatro niveles son opcionales e
independientes entre sí).

## Ejemplos

### Desplazamientos por estado de origen y tipo

```sql
SELECT
    st.name        AS entidad_origen,
    ps.name        AS tamano,
    tp.name        AS temporalidad,
    COUNT(*)       AS n_desplazamientos
FROM df_displacement d
JOIN space_time_state   st ON st.id = d.origin_state_id
JOIN df_populationsize  ps ON ps.id = d.population_size_id
JOIN df_temporality     tp ON tp.id = d.temporality_id
GROUP BY st.name, ps.name, tp.name
ORDER BY n_desplazamientos DESC
```

### Desplazamientos internacionales con país destino

```sql
SELECT
    st.name        AS origen_estado,
    c.name         AS destino_pais,
    COUNT(*)       AS n
FROM df_displacement d
JOIN df_dimension     dim ON dim.id = d.dimension_id
JOIN space_time_state st  ON st.id = d.origin_state_id
LEFT JOIN classify_country c
                          ON c.id = d.destination_country_id
WHERE dim.id = 2   -- internacional
GROUP BY st.name, c.name
ORDER BY n DESC
```

### Desplazamientos ligados a un tipo de afectación

```sql
SELECT
    it.name AS tipo_afectacion,
    COUNT(*) AS n_desplazamientos
FROM df_displacement d
JOIN impact_impact     im ON im.id = d.impact_id
JOIN impact_impacttype it ON it.id = im.impact_type_id
GROUP BY it.name
ORDER BY n_desplazamientos DESC
```

## Trampas frecuentes

- `event_id` e `impact_id` son ambos nullable. Un desplazamiento
  puede estar ligado a uno, al otro o a los dos. Usar `LEFT JOIN`
  cuando cruces con esas tablas, salvo que tu pregunta sea
  específica ("desplazamientos por violencia" → `WHERE event_id IS
  NOT NULL`).
- Para desplazamiento **interno**, el destino está en
  `destination_state/municipality/locality`; `destination_country_id`
  suele ser `NULL`.
- Para desplazamiento **internacional** al revés: el destino vive en
  `destination_country_id` y los campos de estado/municipio/localidad
  de destino suelen ser `NULL`.
- `population_size` tiene `status_validation`; por defecto no se
  filtra.
