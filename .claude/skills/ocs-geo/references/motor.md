# Motor de geolocalización (`api/space_time/geolocate.py`)

Deriva estado, municipio, municipios atravesados, localidad, centroide y conteo de localidades cercanas a partir de la geometría de una `Location`, leyendo la cartografía del INEGI que `load_geometries` dejó en la base (ver [cartografia.md](cartografia.md)). Acuerdo que lo origina: docs `adr-0026`. ADR de cartografía: docs `adr-0029`.

## Entrada y salida

`apply_geolocation(location, geometry_changed=True, write_relations=True) -> list[str]` es la única puerta: escribe sobre el objeto en memoria, devuelve los nombres de los campos que tocó y **no guarda** —quien llama decide entre `save()` y `bulk_update`—. Ramifica por `location.type_location`: `point` va a `_apply_point`, `line` y `polygon` a `_apply_geometry`.

Quiénes la llaman:

- `api/api/views/space_time/serializers.py`, `LocationGeometryMixin._geolocate`: en cada `create` y en los `update` cuya escritura tocó alguno de los campos de geometría (`GEOMETRY_FIELDS`). Una escritura ajena a la geometría no recalcula nada, porque un hueco en `state`/`municipality`/`locality` puede ser deliberado.
- `api/space_time/management/commands/geolocate_locations.py`: backfill (`--review`, `--fill` con respaldo JSON por lote, `--revert`, `--dry-run`).
- `api/api/views/space_time/__init__.py`, acción `GET /location/geolocate/?lat&lon&state`: resuelve al vuelo para el editor, sin escribir.

`write_relations=False` deja el M2M sin escribir pero igual publica la lista en `location.crossed_municipalities` (atributo suelto, no columna): así el backfill puede contarla sin tocar la base y diferir la escritura hasta después de respaldar lo anterior.

## Regla de llenado

`_fill_empty` recorre `FILLABLE = ("state", "municipality", "locality")` y asigna **solo** si el campo está vacío en la ubicación y el motor tiene un valor. Lo capturado a mano nunca se sobrescribe. Un municipio recién llenado arrastra su estado aunque el índice estatal no lo haya resuelto por su cuenta.

Los derivados no siguen esa regla: se reescriben siempre.

| Campo | Punto | Línea / polígono |
|---|---|---|
| `state`, `municipality`, `locality` | solo si están vacíos | solo si están vacíos |
| `municipalities` (M2M) | el municipio resuelto, o lista vacía | todos los atravesados, ordenados de mayor a menor medida |
| `latitude`/`longitude` | dato capturado, no se toca | centroide, reescrito si `geometry_changed` o si estaban vacíos |
| `nearby_localities` | siempre `None` | conteo de localidades tocadas |
| `status_location` | **nunca** | **nunca** |

Si `resolve_geometry` no produce centroide (geojson vacío o ilegible), `_apply_geometry` devuelve `[]` y no escribe nada: no borra lo que hubiera.

## Punto (`resolve_point`)

1. Municipio por point-in-polygon dentro del `state_id` capturado, si lo hay: ahorra la consulta al índice estatal.
2. Si el punto no cae en ningún municipio de ese estado, se resuelve el estado por polígono (`_state_at`) y se reintenta el municipio ahí.
3. El estado sale del municipio resuelto (`municipality.state`), no del índice estatal.
4. Localidad (`_locality_for_point`): primero el polígono de localidad amanzanada (capa `00l`) que contenga al punto; si ninguno lo contiene, el vecino más cercano entre las localidades del municipio con `is_current=True` y coordenadas.

El vecino más cercano es **solo respaldo**, y es el eslabón débil: en una mancha urbana grande que el INEGI representa con un punto único al centro, la localidad rural de al lado suele quedar más cerca que ese centro, y el resultado es una ranchería. Ningún umbral de distancia lo corrige: es un problema del insumo, no de la regla.

## Trazos: línea y polígono (`resolve_geometry`)

**Municipios atravesados** (`_crossed_municipalities`): los candidatos salen del índice estatal por caja envolvente, más el `state_id` capturado si lo hay —un trazo puede cruzar la frontera estatal y el capturado puede estar mal—. De cada candidato se mide la intersección (`_crossing_measure`) y se conserva si pasa el umbral, con el operador `>=`:

| Geometría de la ubicación | Medida | Umbral | Constante |
|---|---|---|---|
| polígono (`geometry.area > 0`) | área de la intersección | ≥ 10 000 m² (1 ha) | `MIN_CROSSING_AREA_M2` |
| línea | longitud de la intersección | ≥ 50 m | `MIN_CROSSING_LENGTH_M` |

El umbral lo decide la geometría de la ubicación, no la de la pieza intersectada: un polígono que solo colinda con el municipio lo corta en una línea de borde, y medirla por longitud lo daría por atravesado. La lista se ordena de mayor a menor medida.

**Municipio base**: `single_municipality` se llena solo si el trazo cruza exactamente uno. Si cruza varios y la ubicación no tiene municipio capturado, queda vacío y lo levanta el filtro «Sin municipio» (`api/space_time/completeness.py`).

**Estado**: no se calcula por polígonos en el caso de trazo; se hereda del municipio base cuando este se llena.

**Localidad** (`_localities_near`): dentro de los municipios atravesados, cuenta como tocada la localidad amanzanada cuyo polígono intersecta el trazo, y la que solo tiene punto de catálogo si ese punto cae dentro del buffer de `LOCALITY_BUFFER_M` = 500 m alrededor del trazo. Una localidad con polígono nunca se mide por su punto: el polígono ya dio la respuesta. Se asigna `locality` **solo si se tocó exactamente una**; el total va a `nearby_localities`, que alimenta un aviso del editor.

**Centroide** (`_centroid`): centroide de shapely para polígonos; para líneas, el punto medio del trazo (`line_interpolate_point` al 0.5 normalizado), porque el centroide de una línea curva cae fuera de ella y el pin del mapa debe estar sobre lo dibujado. Se devuelve `(lat, lon)` en EPSG:4326 redondeado a 6 decimales.

## Proyección

La cartografía y todo el cálculo están en `CRS_METERS = "EPSG:6372"` (Cónica Conforme de Lambert, metros, el CRS nativo del INEGI). Solo se reproyecta la entrada (geojson en `CRS_LATLON = "EPSG:4326"`) y el centroide de salida.

## Caché de índices — gotcha

`_state_index`, `_municipality_index` (por estado), `_locality_index` (por municipio) y `_locality_points` (por municipio) se cachean con `functools.lru_cache` **por proceso y sin invalidación**: recargar la cartografía con `load_geometries` no la refresca. Hay que reiniciar el proceso, o llamar a `clear_indexes()` (lo que hacen los tests). Con varios workers, reiniciar uno no basta.

## Asimetría front / servidor — gotcha

El editor y el servidor no hacen lo mismo con el mismo cálculo:

- **Servidor** (`apply_geolocation`): llena solo lo vacío, en cada guardado que toque la geometría.
- **Editor** (`nuxt/composables/useGeolocate.js`): al soltar o mover el pin de un punto llama a `GET /location/geolocate/` y **sobrescribe los tres selectores**, incluso lo que el usuario ya había elegido; por eso avisa en `LocationAlerts` qué reemplazó.

La divergencia es deliberada —el editor está reaccionando a un gesto explícito del usuario— pero cualquier cambio en una de las dos rutas debe evaluarse contra la otra.

## Tests

`api/space_time/tests/test_geolocate.py`, sobre cartografía sintética (municipios cuadrados de 10 km y localidades inventadas en EPSG:6372): corre sin haber descargado los shapefiles. Cubre resolución por punto, línea y polígono, localidades retiradas del catálogo, el umbral de roce, los municipios atravesados y la regla «solo vacíos». Diagnósticos re-ejecutables en `api/TESTING.md`.
