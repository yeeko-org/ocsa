# TESTING

Estado real del repo, no un ideal: hay **dos suites montadas** —el invariante de escritura de adjuntos, en `source/tests.py`, y el criterio de visibilidad del mapa, en `space_time/tests/`— sobre el runner nativo de Django. Los demás `tests.py` siguen siendo esqueletos vacíos.

Lo demás son **diagnósticos re-ejecutables**: scripts que verifican contra el mundo real (la red, la base) en vez de contra aserciones. Se corren a mano cuando hace falta, no en cada commit.

## Niveles montados

| Nivel | Estado |
|---|---|
| Unitario / integración (`django.test`, runner nativo) | **Sí** — `source` (adjuntos) y `space_time` (visibilidad del mapa, filtros de pendientes y geolocalización) |
| E2E | No montado |
| Diagnósticos manuales | **Sí** — ver abajo |

Sin `pytest` ni `pytest-django`: el runner nativo alcanza para lo que hay y no agrega dependencia. El resto de `task-14` (en `../docs/tasks/`) sigue abierto, incluido mudar a la suite el diagnóstico de política de fallos.

## Suites de tests

### Adjuntos (`source`)

```bash
DATABASE_SCHEMA= python manage.py test source --noinput
```

Ocho tests, ~0.04 s, **sin red y sin costo**: cubren el invariante de escritura de adjuntos de `source/attachment/` —si algo falla, no queda fila `NoteFile` sin archivo real detrás, y los adjuntos previos solo desaparecen cuando el nuevo ya está escrito—. Seis usan un generador de laboratorio (excepción de red, contenido vacío, `build` que devuelve `None`, storage caído al escribir, camino feliz con `replace=True`, y `replace=False` que ni siquiera descarga); dos ejercitan los generadores reales de Reforma y La Jornada con su llamada de red y su render parcheados con `unittest.mock`. El storage no se toca: cada test redirige el campo `NoteFile.file` a un directorio temporal.

### Visibilidad del mapa y geolocalización (`space_time`)

```bash
DATABASE_SCHEMA= python manage.py test space_time --noinput
```

Ciento siete tests, ~1 s, **sin red y sin costo**, repartidos en el paquete `space_time/tests/`:

- `test_map_visibility.py` (7): el criterio único de `adr-0022` —ubicación visible si su estatus y la validación de su proyecto son públicos; proyecto visible si tiene alguna ubicación visible; mención visible si además su nota lo es—. Los helpers viven en `api/views/map/visibility.py`, pero los tests están en `space_time` porque `api/` no es una app instalada y el runner no descubriría sus tests.
- `test_completeness.py` (6): los filtros «Pendientes de ubicación» de `space_time/completeness.py` (`task-69`) — cada opción dice lo mismo consultada por ubicaciones y por proyectos, y `any_pending` es la unión exacta de las demás.
- `test_geolocate.py` (29): el motor `space_time/geolocate.py` (`adr-0026`) sobre **cartografía sintética** —municipios cuadrados de 10 km y localidades inventadas en EPSG:6372—, así que corre sin haber descargado los shapefiles del INEGI: resolución por punto, por línea y por polígono, localidades retiradas del catálogo, localidades marcador «Ninguno» del AGEEML (por punto y por trazo), umbral de roce, municipios atravesados, el tope de 5 km del vecino más cercano —fuera de él el punto se queda sin localidad—, el filtro `is_current` del índice de polígonos, la regla «solo vacíos» de `apply_geolocation` y la salvaguarda que impide llenar la localidad de un punto en «Aprobado (Aproximado)». Cubre también el veto por id de `HUMAN_VERDICTS` (en `space_time/backfill.py`), con su contraprueba.

- `test_legacy_names.py` (10): la resolución de los nombres heredados de `space_time/legacy_names.py`. Nueve son la función pura contra listas de candidatos armadas a mano (qué cuenta como exacto, el umbral difuso, la contención, y qué manda cuando el valor huele a colonia); el décimo va a la base, sobre la cartografía sintética, y comprueba lo único de la consulta al catálogo que puede desalinearse del motor: que las localidades retiradas y los marcadores «Ninguno» no lleguen a ser candidatos.
- `test_backfill_verdicts.py` (14): los dictámenes que el backfill aplica sobre los comentarios `YEEKO:` (`space_time/backfill_verdicts.py`, `task-88`). Reutiliza la cartografía sintética de `test_geolocate.py` (mixin `SyntheticCartography`) y protege lo destructivo: que la reescritura del comentario conserve el texto que escribió un editor, que `details` no repita una referencia que ya dice, que un homónimo vacíe la capa que le toca, que `llenar` no pise un campo ya capturado con otro id, que el último CSV gane sobre el mismo fragmento, que el dictamen corra antes que el motor, y que `HUMAN_VERDICTS` gane incluso sobre un `llenar` del CSV.
- `test_geolocate_endpoint.py` (7): el `POST /api/location/geolocate/` que consume `useGeolocate` en el front, sobre la misma cartografía sintética (reusa `SyntheticCartography`) más un tercer municipio en la entidad ajena: un polígono dentro de un municipio devuelve estado, municipio, la lista de atravesados y el centroide; un trazo interestatal no sugiere estado ni municipio base y devuelve los dos atravesados de mayor a menor medida; la lista `localities` llega hasta 5 km del trazo (entra la que está a 3 km, queda fuera la de 8, y ninguna de las dos lo toca: es la tolerancia del aviso del editor, no el contacto de 500 m con que el motor autollena); y la misma geometría manda como Feature o pelona da la misma respuesta. Dos tests más protegen el contrato de las candidatas que dibuja el front: cada una trae `id`, `name`, `municipality`, `distance_km` y `point`, y el `GET` de un punto las devuelve ordenadas por distancia (0 km la mancha urbana que lo contiene) o vacías cuando la más cercana pasa de 5 km.
- `test_location_owner.py` (3): la regla «toda ubicación cuelga de una ficha» de `LocationGeometryMixin.validate` — se rechaza la que no trae proyecto, evento ni impacto; un patch parcial no vuelve a pedir el dueño que ya está en la instancia; y la edición masiva (`POST /api/location/massive_edit/`) queda exenta, porque su payload trae solo los campos editados.
- `test_location_permission.py` (2): el candado editorial de `LocationPermission` sobre el detalle de la ubicación — el status con `open_editor=False` bloquea a quien no es admin, y la ubicación sin status (nulable, con filas heredadas así) se edita, que es como la lee el dashboard.
- `test_review_flags.py` (29): el marcado editorial de `space_time/review_flags.py` (`task-83`, pendiente 3). Protege lo que no se deshace solo: que repetir la corrida no duplique el comentario aunque cambie la fecha de la firma, que la cuenta de «ya marcadas» vaya por razón y no por entrada (una ubicación con una razón ya comentada y otra nueva suma en las dos), que el estatus se mueva a «Aprobado (con observaciones)» solo desde «Aprobado» y en cualquier otro caso quede intacto, y que `--revert` restaure el estatus previo quitando únicamente el texto agregado, sin llevarse el comentario que ya había escrito un editor. No pasa por la selección de pines contra el municipio (`far_pins.scan`), que necesita la cartografía del INEGI: parte de entradas ya seleccionadas. Las otras selecciones sí corren, sobre la cartografía sintética de `test_geolocate.py`: `trace_off_municipality` (un trazo entero en el municipio vecino sale marcado; uno que apenas roza el capturado no, porque aquí el corte es el contacto y no el umbral de cruce; y uno a 10 m del borde tampoco, por la gracia de `simplified_m`); `base_off_crossed` (ese mismo roce sí sale, porque el corte es la medida del motor); `trace_off_state` (el trazo a 2 km del polígono estatal sale aunque no tenga municipio capturado, y el que está a 20 m no); `trace_in_other_state` (el polígono con la forma del caso 4513 —repartido en su estado capturado y con una parte en el vecino— sale, y el mismo test comprueba que `trace_off_state` lo deja pasar porque su distancia al estado capturado es cero); `trace_off_locality` (el trazo a 8 km de la localidad capturada sale marcado, el que está a 3 km no —tampoco la toca, pero cae dentro de la tolerancia de 5 km—, y la localidad amanzanada se mide contra su polígono); `far_pin_locality` (el pin lejos del punto de catálogo sale marcado; la localidad amanzanada se mide contra su polígono y no contra ese punto, que la daría por lejana; y el pin «Aprobado (Aproximado)» ni entra al universo, aunque sí se mida contra municipio y estado); y `state_mismatch` (el estado capturado que no es el del municipio capturado).

El `DATABASE_SCHEMA=` de los comandos es obligatorio en local: el `.env` apunta al schema `ocsa`, que no existe en la base de test recién creada, y sin vaciarlo la corrida muere en `MigrationSchemaMissing`.

## Diagnósticos disponibles

### Huecos en los lotes de scraping

```bash
python manage.py diagnose_scraping_gaps
python manage.py diagnose_scraping_gaps --source "La Jornada"
```

Solo lectura sobre los `ScrapedRecord` ya registrados. Reporta tres cosas que se confunden entre sí: secciones que el scraper vio pero de las que nunca extrajo artículos (bug de selector), días con secciones caídas por error de acceso, y días sin edición (festivos). Sirve como verificación después de tocar cualquier scraper: una sección marcada `SIEMPRE 0 artículos` es la señal de que un selector dejó de coincidir.

### Acceso a las fuentes (Cloudflare, proxy, TLS)

```bash
# Modo Jornada — matriz completa contra el challenge de Cloudflare
python source/scraper/scraper_access_test.py [YYYY/MM/DD]

# Modo URL genérica — cualquier otra fuente
python source/scraper/scraper_access_test.py <url> [--proxy] [--xml]
```

Distingue cuál de los tres controles de Cloudflare está fallando. Es lo primero que hay que correr ante un 403. Lee `PROXY_KEY` del `.env`.

### Criterio de opinión política (inventario y A/B)

```bash
# Solo lectura: inventario de los artículos vetados por is_political_opinion
python .claude/diagnostics/capped_political_opinion.py            # resumen
python .claude/diagnostics/capped_political_opinion.py jornada    # una fuente
python .claude/diagnostics/capped_political_opinion.py 33954      # un caso

# Llama a Gemini: reclasifica una muestra estratificada de 59 artículos
ROUND=6 python .claude/diagnostics/rerun_political_opinion.py sample   # en seco
ROUND=6 python .claude/diagnostics/rerun_political_opinion.py run
ROUND=6 python .claude/diagnostics/rerun_political_opinion.py report
```

El segundo escribe en `ArticleQualify` con `is_test=True`, **sin tocar** `Article.criteria` ni `certainty_degree`, y es reanudable: salta lo ya calificado con el mismo esquema, así que re-ejecutarlo no vuelve a cobrar. Cada corrida necesita un `ROUND` propio —ancla su `QualifySchema` a un `ScrapedRecord` marcador con fechas de 1900— y acepta `ENGINE` para comparar modelos. Se usó para fijar `adr-0006` y `adr-0007`; el detalle está en `../docs/records/2026-08-01-criterio-de-opinion-politica.md`.

### Política de fallos del ciclo de clasificación

```bash
python .claude/diagnostics/batch_failure_policy.py
```

**El único diagnóstico que no cuesta nada:** no toca la red ni la cuota de Gemini, y revierte la transacción al terminar. Sustituye `RequestGemini` por un doble que falla a voluntad y comprueba las cuatro conductas que fija `adr-0010` (en `../docs/decisions/`) — cortacircuitos a los cinco fallos idénticos, recreación del caché con tope de dos, caída a inline reportada una sola vez, y lote que termina completo pese a fallos sueltos — ejercitando el `build_criteria` real, que desde `task-5` es la única ruta. Sale con código 1 si algo no cuadra.

### Importación de archivos geográficos

```bash
python .claude/diagnostics/geo_import_check.py
```

**Gratis y sin base:** fabrica en un directorio temporal los archivos que llegan del editor (GeoJSON de dos polígonos, shapefile comprimido en EPSG:6372, KML de una y de dos capas, GeoJSON con tipos mezclados, shapefile sin `.prj`, extensión ajena) y verifica el camino `space_time.geo_import.read_geo_file` → `space_time.geometry.normalize_geojson`: reproyección a EPSG:4326, fusión en Multi\*, conservación de atributos y los mensajes de rechazo en español. Sale con código 1 si algo no cuadra. Es la verificación a correr después de tocar `geo_import.py` o el contrato de `geometry.py`.

### Reversibilidad del backfill de geolocalización

```bash
python .claude/diagnostics/geolocate_backup_roundtrip.py [muestra] [dictamen.csv ...]
```

**Gratis y sin red, y no deja rastro en la base:** corre el `--fill` real de `geolocate_locations` sobre las primeras N ubicaciones con geometría, lo revierte con el respaldo JSON que ese mismo comando deja, y compara fila por fila contra la foto previa —incluido el M2M `municipalities`—. Todo dentro de una transacción que se revierte al terminar. Sale con código 1 si alguna ubicación no volvió a su valor previo. Es la verificación a correr antes de un `--fill` de verdad, y después de tocar `space_time/geolocate.py` o el comando. Pasarle los CSV de dictámenes es lo único que ejercita el respaldo de `comments` y `details`: sin ellos esos dos campos nunca cambian.

### Dictamen de los topónimos legados

```bash
python manage.py resolve_legacy_names
python manage.py resolve_legacy_names --project-only --out .claude/legacy_names_verdicts_project.csv
```

**Gratis y sin red, solo lectura:** recorre las ubicaciones cuyo `comments` empieza con `YEEKO:`, parte cada comentario en fragmentos y dictamina cada uno contra el catálogo del INEGI dentro del ámbito capturado (`space_time/legacy_names.py`, `task-88`). No toca la base: escribe un CSV en `.claude/verdicts/legacy_names_verdicts.csv` —el `--out` por omisión— con una fila por fragmento, su nivel de coincidencia y el veredicto (`llenar`, `a_details`, `vaciar`, `sin_resolver`). `--project-only` acota a las ubicaciones ligadas a un proyecto; esa rebanada es la entrada de `.claude/diagnostics/legacy_names_manual.py`, que le pega los 57 dictámenes hechos a mano y regenera `.claude/verdicts/legacy_names_manual_project.csv`. El catálogo de candidatos filtra igual que el motor —localidades vigentes y sin los marcadores «Ninguno» del AGEEML—, así que hay que regenerar el CSV después de tocar ese filtro.

### Backfill con dictámenes aplicados

```bash
python manage.py geolocate_locations --fill --dry-run \
    --verdicts .claude/verdicts/legacy_names_verdicts.csv \
                .claude/verdicts/legacy_names_manual_project.csv \
                .claude/verdicts/yeeko_states_verdicts.csv

python manage.py geolocate_locations --fill \
    --verdicts .claude/verdicts/legacy_names_verdicts.csv \
                .claude/verdicts/legacy_names_manual_project.csv \
                .claude/verdicts/yeeko_states_verdicts.csv \
    --changes-out .claude/geolocate_fill_changes_<fecha>.csv

python manage.py geolocate_locations --revert .claude/geolocate_fill_<fecha>.json
```

**Escribe.** Los tres CSV van en orden de prioridad —el último gana sobre el mismo fragmento—: el automático primero, encima los dictámenes hechos a mano y al final los estados de `yeeko_states_verdicts.csv`. El dictamen corre antes que el motor: lo que un CSV resuelve, el motor ya no lo toca. Antes de la corrida de verdad, `--dry-run` cuenta sin escribir y el diagnóstico de reversibilidad de arriba prueba el camino completo con estos mismos CSV (es lo único que ejercita el respaldo de `comments` y `details`). Cada `--fill` deja su respaldo en `.claude/geolocate_fill_<fecha>.json` y el detalle campo por campo en `.claude/geolocate_fill_changes_<fecha>.csv`; `--revert` deshace la corrida con ese JSON. Los tres CSV de dictámenes sí se versionan (viven en `.claude/verdicts/`): son trabajo humano, no salida regenerable.

### Revisión enriquecida de la geolocalización

```bash
python .claude/diagnostics/geolocate_review_enrich.py
```

**Gratis y sin red, solo lectura:** recorre el mismo universo que `geolocate_locations --review` (ubicaciones con proyecto y con geometría), recalcula la resolución con el motor actual y escribe tres archivos en `.claude/`: `geolocate_review_analizado.csv` (una fila por ubicación donde lo capturado difiere de lo calculado, en español, con población, ámbito urbano/rural y distancias de la localidad capturada y de la calculada), `geolocate_review_raw.jsonl` y `geolocate_review_tally.json`. No necesita correr `--review` antes; lee la base directamente y no escribe en ella. El ámbito lo saca de `space_time/geo_files/localidades.csv` (el AGEEML en disco), así que hace falta haber corrido `download_inegi.sh`. Es lo que hay que regenerar después de tocar `space_time/geolocate.py`, porque la cuenta de filas sostiene lo que dice `../docs/tasks/task-83`.

### Pines lejos de lo capturado

```bash
python .claude/diagnostics/far_pins.py [umbral_km]
```

**Gratis y sin red, solo lectura:** mide con shapely, en EPSG:6372, la distancia de cada ubicación de tipo `point` con proyecto y coordenadas al polígono del municipio capturado y al del estado capturado (0 si el pin cae dentro), y saca en `.claude/far_pins_<fecha>.csv` las filas que rebasan el umbral —2 km por omisión, decisión de Ricardo del 2026-08-28— o que quedan fuera de su estado. Sirve para separar el pin mal puesto de la captura equivocada. La medición vive en `space_time/far_pins.py`, no en el diagnóstico: es la misma que aplica el comando de marcado.

### Comentarios de las ubicaciones que tocaría el backfill

```bash
python .claude/diagnostics/location_comments.py
```

**Gratis y sin red, solo lectura:** replica la selección de `geolocate_locations --fill` corriendo `apply_geolocation` con `write_relations=False` y descartando el objeto, así que no toca ninguna columna ni el M2M. Reporta en stdout cuántas ubicaciones con `comments` no vacío tocaría el fill, desglosadas por tipo, por geometría y por `status_location`, y qué campos llenaría; deja el detalle en `.claude/location_comments_raw.jsonl`. Sirve para decidir la política sobre comentarios humanos antes de un `--fill` de verdad.

### Deformación de los polígonos al simplificarlos

```bash
python .claude/diagnostics/municipality_simplify_area.py [tolerancia]
```

**Gratis y sin base:** lee `00mun.shp` igual que `load_geometries` y compara el área de los 2,478 municipios antes y después de `simplify(tolerancia)`. Reporta cuántos cambian más de 1 %, los diez de mayor cambio relativo y el municipio de área mínima. Es lo que sostiene la elección de `DEFAULT_SIMPLIFIED_M`.

### Recuperación histórica y reclasificación (gastan)

```bash
# Solo scraping, sin tocar Gemini: verifica el HTML antes de pagar IA
python manage.py recover_single_sections --phase scrape --limit-records 1

# Corrida completa de un lote, con clasificación y pre-captura
python manage.py recover_single_sections --limit-records 1 --user <email>

# Reclasificación de los capados, muestra corta y sin segunda pasada
python manage.py reclassify_capped_articles --limit 20 --only-first
```

Ambos son idempotentes: re-correrlos no duplica artículos ni vuelve a
pagar lo ya hecho. `--phase scrape` y `--limit`/`--limit-records` son lo
que sustituye al dry-run, porque el repo no usa transacciones.

Se verifican con los dos diagnósticos de arriba: `diagnose_scraping_gaps`
debe dejar de marcar «Editorial» y «El Correo Ilustrado» como «SIEMPRE 0
artículos» en los días procesados, y `capped_political_opinion` debe
bajar su conteo. Conviene guardar la salida de ambos **antes** de correr:
escribir el JSON `data` borra la evidencia del bug original.

`reclassify_capped_articles` sobrescribe `criteria` y `certainty_degree`
sin guardar el valor previo; el movimiento solo queda en el reporte de
stdout, así que conviene redirigirlo a un archivo.

### Universos de adjuntos por regenerar (task-42)

```bash
python manage.py regenerate_note_files --mode all --dry-run
```

Solo lectura: cuenta las notas de Reforma con portada de sección por regenerar y las notas sin adjunto rellenables, separando las que no tienen `Article` (inalcanzables para el generador). Sin `--dry-run` **escribe**: descarga de la hemeroteca de Reforma (~2 peticiones por nota, sin costo monetario), reemplaza adjuntos y corrige `Note.pages`. Acotar siempre con `--limit` o `--ids` fuera de la corrida planeada.

### Purga de ubicaciones huérfanas del legacy

```bash
python manage.py purge_orphan_locations                      # solo reporta
python manage.py purge_orphan_locations --apply --expect 3103
python manage.py purge_orphan_locations --dashboard-orphans   # agrega las del dashboard
```

Sin `--apply` es solo lectura: reporta cuántas ubicaciones sin proyecto, evento ni impacto colgaban en el legacy de un opositor, de una población afectada o de nada, desglosadas por clase y por estatus. Con `--apply` **borra**. La bandera `--dashboard-orphans` agrega a la selección las ubicaciones sin referencia legacy que nacieron sin padre en el dashboard y no aportan nada —sin dato (sin texto, sin trazo y sin coordenadas: el estado y el municipio solos no salvan la fila), equivalentes a una hermana con padre (mismo texto normalizado o contenido en él, en el mismo estado y municipio; si la huérfana no capturó estado o municipio, basta el texto), o copias dentro de su propio grupo de duplicados—; conserva la primera de cada grupo, que es la que se le pasa al equipo de OCSA para revisión. Necesita la conexión `legacy` configurada (`DATABASE_LEGACY_*` con `DATABASE_LEGACY_SCHEMA=ocs`), porque la selección se recalcula cada vez desde las tablas puente de `ocs` —nunca hay lista de ids fija—, y por eso es idempotente y sirve igual en local que en producción. No deja respaldo a propósito: el schema `ocs` es el respaldo. Antes de borrar comprueba que ninguna fila seleccionada tenga clics, municipios atravesados ni geojson, y `--expect N` aborta si la cuenta se desvía más del 5 % de la corrida en seco. En la copia local del 2026-08-26 seleccionó 3,103 filas, ya aplicadas el 2026-08-28; con `--dashboard-orphans` selecciona 53 más y deja 14 para revisión (el detalle de esas 67, en `.claude/dashboard_orphans_2026-08-28.csv`).

### Marcado editorial de ubicaciones dudosas

```bash
python manage.py flag_locations_for_review                    # solo reporta
python manage.py flag_locations_for_review --apply --expect 222
python manage.py flag_locations_for_review --revert .claude/review_flags_<fecha>.csv
```

Sin `--apply` es solo lectura: recomputa la selección desde los datos —nunca hay lista de ids fija— y deja en `.claude/review_flags_<fecha>.csv` una fila por comentario que agregaría (ubicación, proyecto, clase, estatus antes y después, texto). Con `--apply` **escribe**, en una transacción y con `bulk_update`. Seis clases: `far_pin`, los puntos que el diagnóstico de pines lejanos selecciona (mismo módulo; `--threshold` mueve su umbral, 2 km por omisión); `far_pin_locality` y `trace_off_locality`, el pin y el trazo que quedan a más de 5 km de la localidad capturada (`--locality-threshold`, que **no** hereda de `--threshold`: es el mismo número que el editor aplica en vivo al dibujar, `geolocate.LOCALITY_TOLERANCE_M`); `trace_off_municipality`, el trazo que no toca el polígono del municipio capturado (sin umbral: basta el roce); `state_mismatch`, el estado que no es el del municipio capturado; y `legacy_name`, las dos ubicaciones dictaminadas a mano cuyo nombre de localidad del legado no tiene resolución (12302 «Loreto» y 12643 «Los Napuchis»). Una misma ubicación puede salir por varias clases: cada razón deja su comentario y su fila del CSV, y el estatus se mueve una sola vez. A todas les agrega un comentario fechado y firmado con la convención del front (`\n\n` + `DD/MM/YYYY - Ricardo: texto`); a las que están en «Aprobado» les cambia además el estatus a «Aprobado (con observaciones)», y a las demás no les mueve el estatus, porque ya están en flujo de revisión. Es idempotente: la ubicación cuyo comentario ya contiene el texto se salta. `--expect N` aborta antes de escribir si la selección se desvía más del 5 %. `--revert <csv>` deshace la corrida leyendo ese mismo CSV: restaura el estatus previo y quita solo el texto agregado. En la copia local del 2026-08-26, con los umbrales por omisión (2 km al municipio, 5 km a la localidad) y con las clases `far_pin`, `trace_off_municipality` y `legacy_name` ya aplicadas de corridas anteriores, la corrida del 2026-08-28 marcó 222 ubicaciones más (222 comentarios; 114 cambian de estatus): 195 `far_pin_locality`, 25 `trace_off_locality` y 2 `state_mismatch`, sobre 1,040 puntos con proyecto, 1,173 puntos con localidad, 150 trazos con municipio, 122 trazos con localidad y 7,739 ubicaciones con estado y municipio revisados.

### Sonda de Proceso

`source/tests.py::probe_proceso_sections()` cuenta secciones y artículos de un issue de PressReader. **Hay que llamarla explícitamente** (shell de Django o import); vive dentro de una función justo para que `manage.py test` no la dispare al importar el módulo. Consume slot de sesión de PressReader.

## Credenciales

Todo lo que los diagnósticos necesitan vive en `.env`: `PROXY_KEY` para el scraping vía proxy, `PRESSREADER_USER`/`PRESSREADER_PASS` para Proceso, `GEMINI_API_KEY` para el pipeline de criterios. No hay credenciales de prueba separadas: los diagnósticos golpean servicios reales.

Para entrar al dashboard local en el navegador hacen falta usuarios de la base local: están en `../docs/keys/local-dashboard-credentials.md` (submódulo privado). Ningún valor se escribe fuera de `docs/`.

## Cuidados al ejercitar el pipeline

- **El scraping gasta.** El proxy se cobra por tráfico y PressReader tiene un slot de sesión único; correr diagnósticos en bucle tiene costo real.
- **Los criterios llaman a Gemini.** Cualquier prueba que dispare `build_criteria` en `FirstCriteriaManager` o `PreCaptureManager` consume cuota.
- **La base local (`ocsa-local2`) es una copia de producción y envejece.** Antes de concluir sobre volúmenes actuales, verifica su frescura con `max(capture_date)` de `source_note`; si está vieja, repite el procedimiento completo —dump por SSH sin escribir en el EC2, respaldo local previo, `pg_restore`, `migrate`— del reference `../docs/reference/2026-08-26-copia-de-produccion-a-local.md`. Última copia: 2026-08-26.
