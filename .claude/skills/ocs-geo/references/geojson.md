# Contrato del `geojson` — qué ve el motor

El contrato completo **no vive aquí**. Su sede es el código: el docstring de módulo de `api/space_time/geometry.py` fija el invariante del dato, y ese mismo módulo lo aplica (`normalize_geojson`, `geometry_type_for`, `has_geometry_q`). La tabla de tipo de ubicación × geometría admitida y la explicación del modelo conceptual están en `docs/reference/2026-08-17-ubicaciones-y-geometria.md`, §«El contrato de `geojson`». Este archivo solo recoge lo que el motor de geolocalización necesita saber del contrato y no está formulado como regla operativa en ninguno de los dos.

## Lo que el motor da por cierto

- **Un solo `Feature`** por `Location`, o `null`. El motor nunca recibe una `FeatureCollection`: la normalización de los serializers ya la colapsó a un `Feature` simple o Multi\*. `feature_to_shape` tolera además una geometría desnuda, por si se le llama fuera de esa ruta.
- **`point` no guarda `geojson`.** El punto vive en `latitude`/`longitude`, y por eso `apply_geolocation` ramifica por `type_location` y no por el contenido del `geojson`.
- **En línea y polígono, `latitude`/`longitude` son propiedad del servidor**: no son dato capturado sino el centroide derivado del trazo, que el motor reescribe en cada guardado que toque la geometría. El cliente puede mandarlas; se ignoran.
- **Coordenadas 2D, sin miembro `crs`, en EPSG:4326.** El motor reproyecta a EPSG:6372 al entrar y solo devuelve grados en el centroide. Un `crs` en la entrada sería silenciosamente ignorado, no obedecido.
- **Sin partes vacías ni degeneradas.** Una geometría vacía equivale a «sin geometría»; `feature_to_shape` devuelve `None` y `_apply_geometry` sale sin escribir —no borra lo que ya hubiera—.
- **Multi\* de una sola parte es válido** (QGIS los exporta así): el motor no distingue simple de Multi\*, mide sobre la geometría completa.

## Frontera con el motor

`geometry.py` es Python puro y no depende de GEOS ni de la cartografía: valida y normaliza forma, nada más. Toda decisión sobre *dónde cae* la geometría es de `geolocate.py` (ver [motor.md](motor.md)). No mezclar: una regla de umbral o de cartografía en `geometry.py` rompería su independencia y su suite.
