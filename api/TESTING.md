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

Treinta y dos tests, ~0.23 s, **sin red y sin costo**, repartidos en el paquete `space_time/tests/`:

- `test_map_visibility.py` (7): el criterio único de `adr-0022` —ubicación visible si su estatus y la validación de su proyecto son públicos; proyecto visible si tiene alguna ubicación visible; mención visible si además su nota lo es—. Los helpers viven en `api/views/map/visibility.py`, pero los tests están en `space_time` porque `api/` no es una app instalada y el runner no descubriría sus tests.
- `test_completeness.py` (6): los filtros «Pendientes de ubicación» de `space_time/completeness.py` (`task-69`) — cada opción dice lo mismo consultada por ubicaciones y por proyectos, y `any_pending` es la unión exacta de las demás.
- `test_geolocate.py` (19): el motor `space_time/geolocate.py` (`adr-0026`) sobre **cartografía sintética** —municipios cuadrados de 10 km y localidades inventadas en EPSG:6372—, así que corre sin haber descargado los shapefiles del INEGI: resolución por punto, por línea y por polígono, localidades retiradas del catálogo, umbral de roce, municipios atravesados y la regla «solo vacíos» de `apply_geolocation`.

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
python .claude/diagnostics/geolocate_backup_roundtrip.py [muestra]
```

**Gratis y sin red, y no deja rastro en la base:** corre el `--fill` real de `geolocate_locations` sobre las primeras N ubicaciones con geometría, lo revierte con el respaldo JSON que ese mismo comando deja, y compara fila por fila contra la foto previa —incluido el M2M `municipalities`—. Todo dentro de una transacción que se revierte al terminar. Sale con código 1 si alguna ubicación no volvió a su valor previo. Es la verificación a correr antes de un `--fill` de verdad, y después de tocar `space_time/geolocate.py` o el comando.

### Revisión enriquecida de la geolocalización

```bash
python .claude/diagnostics/geolocate_review_enrich.py
```

**Gratis y sin red, solo lectura:** recorre el mismo universo que `geolocate_locations --review` (ubicaciones con proyecto y con geometría), recalcula la resolución con el motor actual y escribe tres archivos en `.claude/`: `geolocate_review_analizado.csv` (una fila por ubicación donde lo capturado difiere de lo calculado, en español, con población, ámbito urbano/rural y distancias de la localidad capturada y de la calculada), `geolocate_review_raw.jsonl` y `geolocate_review_tally.json`. No necesita correr `--review` antes; lee la base directamente y no escribe en ella. El ámbito lo saca de `space_time/geo_files/localidades.csv` (el AGEEML en disco), así que hace falta haber corrido `download_inegi.sh`. Es lo que hay que regenerar después de tocar `space_time/geolocate.py`, porque la cuenta de filas sostiene lo que dice `../docs/tasks/task-83`.

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

### Sonda de Proceso

`source/tests.py::probe_proceso_sections()` cuenta secciones y artículos de un issue de PressReader. **Hay que llamarla explícitamente** (shell de Django o import); vive dentro de una función justo para que `manage.py test` no la dispare al importar el módulo. Consume slot de sesión de PressReader.

## Credenciales

Todo lo que los diagnósticos necesitan vive en `.env`: `PROXY_KEY` para el scraping vía proxy, `PRESSREADER_USER`/`PRESSREADER_PASS` para Proceso, `GEMINI_API_KEY` para el pipeline de criterios. No hay credenciales de prueba separadas: los diagnósticos golpean servicios reales.

Para entrar al dashboard local en el navegador hacen falta usuarios de la base local: están en `../docs/keys/local-dashboard-credentials.md` (submódulo privado). Ningún valor se escribe fuera de `docs/`.

## Cuidados al ejercitar el pipeline

- **El scraping gasta.** El proxy se cobra por tráfico y PressReader tiene un slot de sesión único; correr diagnósticos en bucle tiene costo real.
- **Los criterios llaman a Gemini.** Cualquier prueba que dispare `build_criteria` en `FirstCriteriaManager` o `PreCaptureManager` consume cuota.
- **La base local (`ocsa-local2`) es una copia de producción y envejece.** Antes de concluir sobre volúmenes actuales, verifica su frescura con `max(capture_date)` de `source_note`; si está vieja, repite el procedimiento completo —dump por SSH sin escribir en el EC2, respaldo local previo, `pg_restore`, `migrate`— del reference `../docs/reference/2026-08-26-copia-de-produccion-a-local.md`. Última copia: 2026-08-26.
