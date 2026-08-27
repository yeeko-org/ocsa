# Entidad: Ubicación (Location)

Dónde está un megaproyecto, un evento o una afectación. Una `Location` cuelga de **un** padre (`project`, `event` o `impact`) y describe un lugar con división administrativa y, opcionalmente, geometría. La fuente canónica y detallada es el reference `2026-08-17-ubicaciones-y-geometria` en `docs/reference/`; aquí va lo indispensable para queries, filtros y exportaciones.

## Modelo `space_time.Location`

- FK nulables: `project`, `event`, `impact` (una sola puesta), `state`, `municipality`, `locality` (una de cada) más el M2M derivado `municipalities` (todos los municipios que atraviesa la geometría, incluido el base) y `nearby_localities`.
- **Derivación geográfica y cartografía del INEGI: skill `ocs-geo`** — reglas, umbrales, loaders y contrato del `geojson` viven allí, no aquí.
- `type_location`: choices `point` | `line` | `polygon` (`TYPE_LOCATIONS`; no es tabla). El 2026-08-26 se reabrió como tarea futura darle su propio modelo `LocationType` y renombrar el campo a `location_type`.
- `latitude`, `longitude`: en `point`, la coordenada capturada; en `line` y `polygon`, el centroide que calcula el servidor al guardar la geometría (punto medio del trazo en las líneas).
- `geojson` (JSONField): `null` o **un** `Feature` GeoJSON — `line` → `LineString`/`MultiLineString`, `polygon` → `Polygon`/`MultiPolygon`; `point` no guarda geojson. 2D, sin `crs`, sin partes vacías. Contrato y normalización en `api/space_time/geometry.py`; los serializers lo aplican en toda escritura.
- `status_location`: FK a `work_flux.StatusControl` grupo `location`. Juicio humano: `finished` «Aprobado», `Aproximado`, `need_consensus`, `filled` «Datos completos»; ninguna regla los mueve. `Project.status_location` se deriva de estas —el mínimo— y **no es editable** desde `adr-0027` (`api/utils/universal.py`, `apply_project_status_location`): es indicador del dashboard y no interviene en el mapa público.
- `ubicacion_id_ref`: pk en la tabla legacy `ocs.ubicaciones`; `details`, `comments`.

## Consultas típicas

- «Tiene geometría»: usa siempre `space_time.geometry.has_geometry_q(prefix)` (par lat/lon **o** geojson) — nunca reimplementes la condición.
- Pendientes de ubicación (filtro «Pendientes de ubicación», sustituye a los cajones de completitud): `space_time.completeness` — `location_pending_q(option)` sobre `Location`, `project_pending_q(option)` sobre `Project`. Opciones: `no_geometry` «Sin marca en el mapa», `no_municipality` «Sin municipio», `complete_unapproved` «Completas sin aprobar», `any_pending` «Alguno de los casos anteriores»; proyectos suma `no_approved_location` «Sin ninguna ubicación aprobada». No son disjuntas: una ubicación puede caer en varias. Solo cuentan ubicaciones de proyecto, y a nivel proyecto siempre se aplican por subconsulta (`locations__in=...`) para que las condiciones caigan sobre la misma ubicación.
- Mapa público: `/project_location/` emite un `Feature` por `Location` con `properties` `id, state, municipality, locality, project`; una `Location` Multi* sigue siendo una feature.
- Exportación XLSX (`api/api/export_blocks/location.py`): solo `loc_latitude`/`loc_longitude`; en líneas y polígonos salen con el centroide calculado.

## Visibilidad del mapa público

Criterio **único**, en `api/api/views/map/visibility.py` (`adr-0022`): `visible_locations`, `visible_projects(qs, path)`, `visible_mentions(qs, path)` — nunca reimplementarlo. Ubicación visible = su `status_location` es público **y** la validación de su proyecto también; proyecto visible = validación pública **y** al menos una ubicación pública; mención visible = lo anterior **y** nota pública. El `status_location` del proyecto no participa (`adr-0027`). Lo consumen los pines, `project_map` y el índice de facetas/actores; ninguno guarda criterio propio. Cubierto por `manage.py test space_time`.

## Entrada de geometría

- Editor del dashboard: mapbox-gl-draw; varias figuras del mismo tipo se ensamblan en un Multi*.
- Cada tipo lleva en `nuxt/composables/location_types.js` su `draw_mode` de mapbox-gl-draw y su `draw_icon`; el botón «Agregar …» del editor arranca el dibujo explícitamente — nunca se activa solo.
- Importación: `POST /api/location/import_geo/` (GeoJSON, shapefile en zip, KML; `pyogrio` + `shapely` + `pyproj`); devuelve la geometría normalizada y no escribe.
