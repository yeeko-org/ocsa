# Ubicaciones geográficas

La base maneja dos familias de tablas:

- **Catálogos INEGI** (`space_time_state`, `space_time_municipality`,
  `space_time_locality`): la división político-administrativa de
  México.
- **Ubicaciones registradas** (`space_time_location`): filas concretas
  que ligan una ubicación (estado, municipio, localidad, punto
  geográfico) con un proyecto, evento o afectación.

## Catálogos INEGI

### `space_time_state`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `inegi_code` | char(2) | Código INEGI de la entidad |
| `name` | text | Nombre oficial |
| `short_name` | text | Nombre corto |
| `code_name` | text | Abreviatura (tres letras) |
| `alternative_names` | jsonb | Lista de nombres alternativos |

### `space_time_municipality`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `state_id` | integer → `space_time_state.id` | |
| `inegi_code` | char(6) | Clave de municipio |
| `complete_code` | char(8) | Clave estado-municipio (ej. `01-001`) |
| `name` | text | |
| `std_name` | text | Nombre normalizado (sin acentos) |
| `population` | integer | Población total |
| `latitude` | float | Cabecera municipal |
| `longitude` | float | Cabecera municipal |
| `altitude` | integer | |

### `space_time_locality`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `municipality_id` | integer → `space_time_municipality.id` | |
| `inegi_code` | char(6) | Clave de localidad |
| `complete_code` | char(12) | Clave estado-municipio-localidad |
| `name` | text | |
| `population` | integer | |
| `is_rural` | bool | |
| `latitude` | float | |
| `longitude` | float | |
| `altitude` | integer | |

## Ubicaciones registradas

### `space_time_location`

Fila que ata una entidad (proyecto / evento / afectación) con un
punto, municipio o localidad concreta. Las tres FKs a las entidades
padre son nullable y, en la práctica, cada fila pertenece a una sola.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | integer | PK |
| `project_id` | integer → `project_project.id` | (nullable) |
| `event_id` | integer → `event_event.id` | (nullable) |
| `impact_id` | integer → `impact_impact.id` | (nullable) |
| `state_id` | integer → `space_time_state.id` | (nullable) |
| `municipality_id` | integer → `space_time_municipality.id` | (nullable) |
| `locality_id` | integer → `space_time_locality.id` | (nullable) |
| `latitude` | float | Punto preciso si lo hay |
| `longitude` | float | |
| `geojson` | jsonb | Polígono o línea, si aplica |
| `type_location` | text | `point`, `polygon`, `line` |
| `details` | text | Texto libre |
| `comments` | text | Observaciones editoriales |
| `status_location_id` | text → `work_flux_statuscontrol.name` | Estatus de validación de la ubicación |

## Patrón canónico: "ubicación principal" de una entidad

Cuando una entidad (proyecto, evento, afectación) tiene varias filas
en `space_time_location`, se elige la de **mayor
`status_location.priority`**. La `priority` vive en
`work_flux_statuscontrol` (FK por nombre).

PostgreSQL permite resolverlo con `DISTINCT ON`:

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
LEFT JOIN space_time_location lo   ON lo.project_id = p.id
LEFT JOIN work_flux_statuscontrol sc
                                    ON sc.name = lo.status_location_id
LEFT JOIN space_time_state        st  ON st.id  = lo.state_id
LEFT JOIN space_time_municipality mun ON mun.id = lo.municipality_id
LEFT JOIN space_time_locality     loc ON loc.id = lo.locality_id
ORDER BY p.id, sc.priority DESC NULLS LAST
```

Equivalente usando subconsulta (útil si se quiere anotar columnas
sueltas sin perder otras filas de la consulta principal):

```sql
SELECT
    p.id,
    p.name,
    (SELECT st.name
       FROM space_time_location lo2
       JOIN space_time_state    st ON st.id = lo2.state_id
       LEFT JOIN work_flux_statuscontrol sc2
             ON sc2.name = lo2.status_location_id
      WHERE lo2.project_id = p.id
      ORDER BY sc2.priority DESC NULLS LAST
      LIMIT 1) AS entidad_principal
FROM project_project p
```

Aplica igual para `event_id` e `impact_id`.

## Ejemplos

### Proyectos con su entidad (ubicación principal)

Ver el primer bloque de SQL arriba.

### Ubicación del evento con fallback al proyecto

Si el evento no tiene ubicación propia, usar la del proyecto asociado.

```sql
SELECT
    ev.id,
    ev.date,
    COALESCE(
        st_ev.name,
        st_pr.name
    ) AS entidad
FROM event_event ev
LEFT JOIN space_time_location lo_ev ON lo_ev.event_id = ev.id
LEFT JOIN space_time_state    st_ev ON st_ev.id = lo_ev.state_id
LEFT JOIN source_mention      m     ON m.id = ev.mention_id
LEFT JOIN space_time_location lo_pr ON lo_pr.project_id = m.project_id
LEFT JOIN space_time_state    st_pr ON st_pr.id = lo_pr.state_id
```

(Para producción, envolver las dos `space_time_location` con el
criterio de `priority` del patrón canónico.)

## Trampas frecuentes

- `space_time_location` registra la ubicación de **una** entidad por
  fila. Filtrar siempre por la FK correspondiente
  (`project_id`, `event_id` o `impact_id`).
- Cuando se busca "la" ubicación y hay varias, elegir por
  `status_location.priority`. Sin ese criterio, el resultado puede
  variar entre ejecuciones.
- **Desplazamiento forzado no usa `space_time_location`**: sus
  ubicaciones viven en columnas propias de `df_displacement`. Ver
  `df.md`.
- `state_id`, `municipality_id`, `locality_id` son **todas**
  nullable. Una ubicación puede estar registrada solo a nivel de
  estado (municipio y localidad en NULL), o incluir localidad sin
  datos precisos de municipio.
- `status_location_id` guarda el `name` (texto) del `StatusControl`.
