---
name: ocs-geo
description: Reglas operativas de la geolocalización de OCSA — motor que deriva estado, municipio, municipios atravesados, localidad y centroide de una `Location`; cartografía del INEGI (Marco Geoestadístico, AGEEML) y sus loaders; contrato del `geojson`. Activar al tocar `space_time/geolocate.py`, umbrales de intersección, `load_geometries`/`load_municipios`/`load_localidades`, los shapefiles de `geo_files/`, el endpoint `/location/geolocate/` o el composable `useGeolocate`.
---

# OCS Geo — índice de referencias

Sede canónica de las reglas y parámetros de la geolocalización: si el código y estos archivos discrepan, gana el código y se corrige aquí.

| Tema | Archivo | Cuándo cargarlo |
|---|---|---|
| Motor de derivación | [motor.md](references/motor.md) | Umbrales, regla de llenado, resolución de punto y de trazo, caché de índices, asimetría front/servidor |
| Cartografía e insumos INEGI | [cartografia.md](references/cartografia.md) | Descarga, capas, modelos `*Geometry`, orden de carga, idempotencia, `is_current` |
| Contrato del `geojson` | [geojson.md](references/geojson.md) | Qué acepta y normaliza `space_time/geometry.py`, y qué de eso ve el motor |

Restricciones permanentes:

- **Sin PostGIS.** Todo el cálculo es shapely en memoria del proceso, sobre WKB en EPSG:6372 guardado en modelos 1:1; no introducir dependencias GIS en la base de datos.
- **Solo se llena lo vacío.** El servidor nunca sobrescribe `state`, `municipality` o `locality` capturados a mano, y ningún automatismo toca `status_location` (docs `adr-0024`, `adr-0027`).
- **Los derivados se reescriben siempre**: el M2M `municipalities` y el centroide se recalculan cuando cambia la geometría; no son capturables.
- **Los umbrales viven en el código**, como constantes de `api/space_time/geolocate.py`; cambiarlos es decisión de Ricardo y se refleja aquí y en docs `adr-0026`.
