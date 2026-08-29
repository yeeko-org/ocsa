# Motor de geolocalización (`api/space_time/geolocate.py`)

Deriva estado, municipio, municipios atravesados, localidad y centroide a partir de la geometría de una `Location`, leyendo la cartografía del INEGI que `load_geometries` dejó en la base (ver [cartografia.md](cartografia.md)). Acuerdo que lo origina: docs `adr-0026`. ADR de cartografía: docs `adr-0029`.

## Entrada y salida

`apply_geolocation(location, geometry_changed=True, write_relations=True) -> list[str]` es la única puerta: escribe sobre el objeto en memoria, devuelve los nombres de los campos que tocó y **no guarda** —quien llama decide entre `save()` y `bulk_update`—. Ramifica por `location.type_location`: `point` va a `_apply_point`, `line` y `polygon` a `_apply_geometry`.

Quiénes la llaman:

- `api/api/views/space_time/serializers.py`, `LocationGeometryMixin._geolocate`: en cada `create` y en los `update` cuya escritura tocó alguno de los campos de geometría (`GEOMETRY_FIELDS`). Una escritura ajena a la geometría no recalcula nada, porque un hueco en `state`/`municipality`/`locality` puede ser deliberado.
- `api/space_time/backfill.py`, que el comando `geolocate_locations` solo envuelve (el comando es puro parseo de argumentos; el módulo es lo que importan tests y diagnósticos): backfill (`--review`, `--fill` con respaldo JSON por lote, `--revert`, `--dry-run`). Ambos modos pasan por `apply_and_diff`, que corre el motor en memoria sin escribir: `--review` solo reporta lo que cambiaría (columnas `cambios_fill` y `cambios_fill_n` del CSV, que sale con **todas** las ubicaciones con proyecto y geometría, cambien o no; las columnas `*_capturado`/`*_calculado` llevan el `name` pelón de la entidad, no su `__str__`, porque cada nivel ya tiene columna propia), `--fill` además respalda y guarda.
- `api/api/views/space_time/__init__.py`, acción `/location/geolocate/`: resuelve al vuelo para el editor, sin escribir, sobre una ubicación que puede no existir aún. No pasa por `apply_geolocation` sino por los resolutores directos. Dos verbos:
  - `GET ?lat&lon&state` → `{state, municipality, locality}`, vía `resolve_point`.
  - `POST {"geojson": <Feature o geometría>, "state": <id|null>}` → `{state, municipality, locality, municipalities: [{id, name, state}], localities: [{id, name, municipality}], centroid: {latitude, longitude}}`, vía `resolve_geometry`; el cuerpo, porque una línea o un polígono no cabe en la query string. `municipality` es el base (solo si el trazo cae en uno) y `state` sale del helper `_geometry_state`: el del municipio base, o el que comparten **todos** los atravesados; si discrepan, `null`, porque elegir sería capturar por el usuario. La lista `localities` **no** es la del motor: se recalcula con `localities_within(geometry, municipalities, LOCALITY_TOLERANCE_M)` y trae las localidades a 5 km o menos del trazo, porque alimenta un aviso al editor y no el autollenado.

`write_relations=False` deja el M2M sin escribir pero igual publica la lista en `location.crossed_municipalities` (atributo suelto, no columna): así el backfill puede contarla sin tocar la base y diferir la escritura hasta después de respaldar lo anterior.

## Regla de llenado

`_fill_empty` recorre `FILLABLE = ("state", "municipality", "locality")` y asigna **solo** si el campo está vacío en la ubicación y el motor tiene un valor. Lo capturado a mano nunca se sobrescribe. Un municipio recién llenado arrastra su estado aunque el índice estatal no lo haya resuelto por su cuenta.

`_blocked_fields` agrega una salvaguarda por estatus: en un **punto** cuyo `status_location` es `Aproximado` («Aprobado (Aproximado)») no se llena `locality` —la coordenada señala el rumbo y no el sitio, así que la localidad sería una precisión falsa—; `state` y `municipality` sí se llenan si están vacíos. Se compara contra `status_location_id`, que en `StatusControl` es el nombre interno (llave primaria), no el `public_name` editable. La salvaguarda no aplica a trazos: ahí la localidad sale de la intersección con la geometría, no de una coordenada dudosa. Decidida por Ricardo el 2026-08-27 en docs `task-83`.

`--verdicts` suma a la pasada los dictámenes humanos sobre los comentarios `YEEKO:` que dejó la migración legada (`space_time/backfill_verdicts.py`, docs `task-88`). Se aplican **antes** del motor —un municipio recién dictaminado ya está puesto cuando la geometría resuelve la localidad— y con la misma regla de «solo lo vacío»; cuando lo capturado contradice al dictamen, el fragmento se queda en el comentario porque es la única constancia del desacuerdo. Cada fragmento atendido desaparece de la línea `YEEKO:`, que se reconstruye con lo que quedó; si no queda nada, la línea se va y sobrevive intacto lo que un editor escribió después. `comments` y `details` viajan en `BACKUP_FIELDS`, de modo que un solo `--revert` deshace limpieza y backfill juntos. Los dictámenes amplían el universo: el motor solo alcanza las ubicaciones con geometría y la limpieza llega a las 3 151 que traen comentario legado.

`HUMAN_VERDICTS`, en `space_time/backfill.py`, es una excepción del backfill y no del motor: un diccionario `{id: (campos vetados,)}` que `apply_and_diff` aplica después de correr el motor, devolviendo el campo a su valor previo y quitándolo de lo tocado. Vale por igual para `--review` (el campo deja de aparecer en `cambios_fill`) y para `--fill` (no se escribe), y gana también sobre un `llenar` de los CSV de dictámenes. Existe porque hay filas donde un humano ya dictaminó lo que el motor no puede saber: la 12716 (Mina El Arco, proyecto 708) tiene un comentario, verificado en QGIS el 2026-08-27, de que ahí no hay ninguna localidad, y el motor le pondría la del vecino más cercano. Su municipio sí se llena.

Los derivados no siguen esa regla: se reescriben siempre.

| Campo | Punto | Línea / polígono |
|---|---|---|
| `state`, `municipality` | solo si están vacíos | solo si están vacíos |
| `locality` | solo si está vacío, y nunca si el estatus es `Aproximado` | solo si está vacío |
| `municipalities` (M2M) | **siempre vacío**: un punto no atraviesa nada | todos los atravesados, ordenados de mayor a menor medida |
| `latitude`/`longitude` | dato capturado, no se toca | centroide, reescrito si `geometry_changed` o si estaban vacíos |
| `status_location` | **nunca** | **nunca** |

Si `resolve_geometry` no produce centroide (geojson vacío o ilegible), `_apply_geometry` devuelve `[]` y no escribe nada: no borra lo que hubiera.

## Punto (`resolve_point`)

1. Municipio por point-in-polygon dentro del `state_id` capturado, si lo hay: ahorra la consulta al índice estatal.
2. Si el punto no cae en ningún municipio de ese estado, se resuelve el estado por polígono (`_state_at`) y se reintenta el municipio ahí.
3. El estado sale del municipio resuelto (`municipality.state`), no del índice estatal.
4. Localidad (`_locality_for_point`): primero el polígono de localidad amanzanada (capa `00l`) que contenga al punto; si ninguno lo contiene, el vecino más cercano entre las localidades del municipio con `is_current=True` y coordenadas.

## Localidades marcador («Ninguno»)

El AGEEML usa el nombre **«Ninguno»** como marcador de localidad sin nombre —ranchos, predios y campos sueltos—, no como topónimo: son 1,610 filas del catálogo (1,114 vigentes, 3 con polígono). Ninguna ubicación debe recibir una de ellas, así que quedan fuera de **todo** conjunto de candidatos del motor: `_locality_index` (polígonos), `_locality_points` (vecino más cercano del punto) y las localidades por punto de `_localities_near` y `localities_within` (trazos), que comparten el helper `_catalog_localities`. La regla vive en un solo lugar, la constante `PLACEHOLDER_LOCALITY_NAMES` y el helper `without_placeholders(queryset, field)` de `geolocate.py`. La exclusión es por nombre **exacto**: las variantes con calificador —«Ninguno [ACUMEX]», «Ninguno (El Doc) [Rancho]»— siguen siendo candidatas, porque ahí el paréntesis o el corchete es el nombre real del lugar. Decidida por Ricardo el 2026-08-28.

El M2M `municipalities` de un punto queda **vacío**, y si traía algo se limpia: la lista significa «municipios que la geometría atraviesa» (docs `adr-0026`) y un punto no atraviesa ninguno; copiar ahí su propio municipio solo duplicaba el FK. El editor ya oculta la tira cuando la lista viene vacía (`LocationMunicipalities.vue`, que con un solo estado lista los chips y con varios abre un renglón por estado). La lista llega como `municipalities_full`, que emiten tanto `LocationGeometryMixin` como los serializers anidados de `Location` (proyecto, evento y nota), y que `suggestGeometry` escribe en memoria para la previsualización.

El vecino más cercano es **solo respaldo**, y es el eslabón débil: en una mancha urbana grande que el INEGI representa con un punto único al centro, la localidad rural de al lado suele quedar más cerca que ese centro, y el resultado es una ranchería. Ningún umbral de distancia lo corrige: es un problema del insumo, no de la regla.

## Trazos: línea y polígono (`resolve_geometry`)

Lo consumen `_apply_geometry` (al guardar) y el `POST /location/geolocate/` (previsualización del editor): el cálculo es uno solo y lo que cambia es quién escribe el resultado.

**Municipios atravesados** (`_crossed_municipalities`): los candidatos salen del índice estatal por caja envolvente, más el `state_id` capturado si lo hay —un trazo puede cruzar la frontera estatal y el capturado puede estar mal—. De cada candidato se mide la intersección (`_crossing_measure`) y se conserva si pasa el umbral, con el operador `>=`:

| Geometría de la ubicación | Medida | Umbral | Constante |
|---|---|---|---|
| polígono (`geometry.area > 0`) | área de la intersección | ≥ 10 000 m² (1 ha) | `MIN_CROSSING_AREA_M2` |
| línea | longitud de la intersección | ≥ 50 m | `MIN_CROSSING_LENGTH_M` |

El umbral lo decide la geometría de la ubicación, no la de la pieza intersectada: un polígono que solo colinda con el municipio lo corta en una línea de borde, y medirla por longitud lo daría por atravesado. La lista se ordena de mayor a menor medida.

**Municipio base**: `single_municipality` se llena solo si el trazo cruza exactamente uno. Si cruza varios y la ubicación no tiene municipio capturado, queda vacío y lo levanta el filtro «Sin municipio» (`api/space_time/completeness.py`).

**Estado**: no se calcula por polígonos en el caso de trazo; se hereda del municipio base cuando este se llena. El endpoint agrega un caso que el motor no tiene: sin municipio base, sugiere el estado si todos los atravesados coinciden (`_geometry_state`).

**Localidad** (`_localities_near`): dentro de los municipios atravesados, cuenta como tocada la localidad amanzanada cuyo polígono intersecta el trazo, y la que solo tiene punto de catálogo si ese punto cae dentro del buffer de `LOCALITY_BUFFER_M` = 500 m alrededor del trazo. Una localidad con polígono nunca se mide por su punto: el polígono ya dio la respuesta. Se asigna `locality` **solo si se tocó exactamente una**; con cero o con varias queda vacía. El conteo no se persiste: hubo un campo `nearby_localities` que lo guardaba y Ricardo lo retiró el 2026-08-28 (migración `space_time.0003`) por ser un derivado que nadie había aprobado.

## Tolerancia de localidad para revisar, no para llenar

Autollenar y avisar no se miden igual, y la diferencia es deliberada. `_localities_near` (500 m, `LOCALITY_BUFFER_M`) exige **contacto** y es lo único que decide qué `locality` se escribe: es la regla de docs `adr-0026` y no cambió. Todo lo que solo *señala* algo a un editor —el aviso en vivo del formulario y el marcado editorial— usa **distancia** y tolera hasta 5 km, en la constante única `LOCALITY_TOLERANCE_M = 5_000` de `geolocate.py`. Ricardo la fijó el 2026-08-28, y ese número vale por igual para pines y para trazos, para que la marca no diga otra cosa que la pantalla.

`localities_within(geometry, municipalities, buffer_m=LOCALITY_TOLERANCE_M)` es la función que lo implementa del lado del trazo: mide contra el polígono de la localidad amanzanada y contra el punto del catálogo AGEEML cuando no hay polígono —el mismo criterio que `far_pins` aplica al pin—, y de ella sale la lista `localities` del `POST`. Al elegir el umbral importa que las dos medidas no son equivalentes: la distancia a un punto de catálogo incluye el radio de la localidad y la distancia a su polígono no.

El marcado editorial (`space_time/review_flags.py`, comando `flag_locations_for_review`) tiene bandera propia, `--locality-threshold`, con 5 km por omisión y **sin herencia** de `--threshold` —que son los 2 km del pin contra su municipio—. Sus dos razones de localidad son `far_pin_locality` (el pin a más de 5 km de la localidad capturada) y `trace_off_locality` (el trazo a más de 5 km de ella, medido por distancia: **no** consulta el veredicto del motor a 500 m). Contra el municipio no hay tolerancia para el trazo: `trace_off_municipality` sale con intersección vacía, sin umbral.

**Asimetría conocida** (2026-08-28, sin resolver): `localities_within` solo mira localidades de los municipios que el trazo atraviesa, y el marcado mide la localidad capturada sin ese filtro. Una localidad a 3 km del trazo en un municipio no atravesado hace que el editor avise y que el marcado calle. Anotada como punto abierto en docs `task-97`.

**Centroide** (`_centroid`): centroide de shapely para polígonos; para líneas, el punto medio del trazo (`line_interpolate_point` al 0.5 normalizado), porque el centroide de una línea curva cae fuera de ella y el pin del mapa debe estar sobre lo dibujado. Se devuelve `(lat, lon)` en EPSG:4326 redondeado a 6 decimales.

## Proyección

La cartografía y todo el cálculo están en `CRS_METERS = "EPSG:6372"` (Cónica Conforme de Lambert, metros, el CRS nativo del INEGI). Solo se reproyecta la entrada (geojson en `CRS_LATLON = "EPSG:4326"`) y el centroide de salida.

## Caché de índices — gotcha

`_state_index`, `_municipality_index` (por estado), `_locality_index` (por municipio) y `_locality_points` (por municipio) se cachean con `functools.lru_cache` **por proceso y sin invalidación**: recargar la cartografía con `load_geometries` no la refresca. Hay que reiniciar el proceso, o llamar a `clear_indexes()` (lo que hacen los tests). Con varios workers, reiniciar uno no basta.

## Asimetría front / servidor — gotcha

El editor y el servidor no hacen lo mismo con el mismo cálculo:

- **Servidor** (`apply_geolocation`): llena solo lo vacío, en cada guardado que toque la geometría.
- **Editor, punto** (`useGeolocate.suggest`): al soltar o mover el pin llama a `GET /location/geolocate/` y **sobrescribe los tres selectores**, incluso lo que el usuario ya había elegido; por eso avisa en `LocationAlerts` qué reemplazó.
- **Editor, trazo** (`useGeolocate.suggestGeometry`): al dibujar, editar o importar una línea o un polígono llama al `POST` con debounce de 400 ms y **solo llena selectores vacíos** —la misma regla del servidor—, así que nunca avisa de un reemplazo. Sí avisa, sin bloquear, cuando lo ya capturado no cuadra con el trazo: el municipio capturado que no está entre los atravesados, y la localidad capturada que no viene en `localities`, es decir la que quedó a más de 5 km («está a más de 5 km del trazo»). Además escribe `municipalities_full` en el registro en memoria para que `LocationMunicipalities` muestre la tira de municipios abarcados antes de guardar. Ambos caminos salen del mismo `applyFeatureAndSuggest` de `LocationEdit.vue`, que ramifica por `type_location`.

La divergencia del pin es deliberada —el editor está reaccionando a un gesto explícito del usuario, y el trazo no la hereda— pero cualquier cambio en una de las rutas debe evaluarse contra las otras.

## Tests

`api/space_time/tests/test_geolocate.py`, sobre cartografía sintética (municipios cuadrados de 10 km y localidades inventadas en EPSG:6372): corre sin haber descargado los shapefiles. Cubre resolución por punto, línea y polígono, localidades retiradas del catálogo, las localidades marcador «Ninguno» (por punto y por trazo), el umbral de roce, los municipios atravesados, el M2M vacío del punto, la regla «solo vacíos», la salvaguarda del punto aproximado y el veto de `HUMAN_VERDICTS`.

El paquete `space_time` corre 90 tests en total (`DATABASE_SCHEMA= python manage.py test space_time`).

El endpoint, el marcado y el editor tienen los suyos, porque su regla no es la del motor:

- `api/space_time/tests/test_geolocate_endpoint.py` (4), sobre la misma cartografía sintética (`SyntheticCartography`): el `POST` sugiere estado y municipio de un polígono contenido en uno, no sugiere estado cuando el trazo cruza dos, acepta por igual un `Feature` y una geometría pelona, y devuelve en `localities` la que está a 3 km del trazo pero no la que está a 8 —ninguna de las dos lo toca, así que el caso separa la tolerancia de 5 km del contacto de 500 m—.
- `api/space_time/tests/test_review_flags.py` (19): las seis razones del marcado editorial, incluidas `far_pin_locality`, `trace_off_locality` (medida contra el polígono de la localidad amanzanada y contra el punto de catálogo cuando no lo hay) y `state_mismatch`. `far_pin` no corre porque su selección necesita la cartografía del INEGI.
- `nuxt/composables/__tests__/useGeolocate.test.js` (5 de los 8 del front): `suggestGeometry` solo llena vacíos, `suggestGeometry(null)` cancela el debounce y vacía `municipalities_full`, el aviso del municipio fuera del trazo se retira al corregirlo, el de la localidad lejana dice los 5 km, y `suggest` (punto) sobrescribe y avisa.

Diagnósticos re-ejecutables en `api/TESTING.md`.
