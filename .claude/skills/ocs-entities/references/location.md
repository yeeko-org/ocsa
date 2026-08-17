# Entidad: Ubicación (Location)

Dónde está un megaproyecto, un evento o una afectación. Una `Location` cuelga de **un** padre (`project`, `event` o `impact`) y describe un lugar con división administrativa y, opcionalmente, geometría. La fuente canónica y detallada es el reference `2026-08-17-ubicaciones-y-geometria` en `docs/reference/`; aquí va lo indispensable para queries, filtros y exportaciones.

## Modelo `space_time.Location`

- FK nulables: `project`, `event`, `impact` (una sola puesta), `state`, `municipality`, `locality` (una de cada; el caso de ubicaciones que cruzan varios municipios está en diálogo, task-51 en docs).
- `type_location`: choices `point` | `line` | `polygon` (`TYPE_LOCATIONS`; no es tabla).
- `latitude`, `longitude`: solo para `point`.
- `geojson` (JSONField): `null` o **un** `Feature` GeoJSON — `line` → `LineString`/`MultiLineString`, `polygon` → `Polygon`/`MultiPolygon`; `point` no guarda geojson. 2D, sin `crs`, sin partes vacías. Contrato y normalización en `api/space_time/geometry.py`; los serializers lo aplican en toda escritura.
- `status_location`: FK a `work_flux.StatusControl` grupo `location`. Juicio humano: `finished` «Aprobado», `Aproximado`, `need_consensus`, `filled` «Datos completos»; ninguna regla los mueve. El proyecto hereda el peor estatus de sus ubicaciones (`api/utils/universal.py`).
- `ubicacion_id_ref`: pk en la tabla legacy `ocs.ubicaciones`; `details`, `comments`.

## Consultas típicas

- «Tiene geometría»: usa siempre `space_time.geometry.has_geometry_q(prefix)` (par lat/lon **o** geojson) — nunca reimplementes la condición.
- Completitud (estado + municipio + geometría): `space_time.completeness.complete_q()` y los cajones `complete_unpromoted` / `incomplete_unpromoted` / `approved_incomplete` (`completeness_q(bucket)`); a nivel proyecto, `locations__in=Location.objects.filter(...)`.
- Mapa público: `/project_location/` emite un `Feature` por `Location` con `properties` `id, state, municipality, locality, project`; una `Location` Multi* sigue siendo una feature.
- Exportación XLSX (`api/api/export_blocks/location.py`): solo `loc_latitude`/`loc_longitude`; líneas y polígonos salen vacíos (centroide pendiente, task-53).

## Entrada de geometría

- Editor del dashboard: mapbox-gl-draw; varias figuras del mismo tipo se ensamblan en un Multi*.
- Importación: `POST /api/location/import_geo/` (GeoJSON, shapefile en zip, KML; `pyogrio` + `shapely` + `pyproj`); devuelve la geometría normalizada y no escribe.
