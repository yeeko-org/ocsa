# TESTING

Estado real del repo, no un ideal: hay **una sola suite montada** —el invariante de escritura de adjuntos, en `source/tests.py`— sobre el runner nativo de Django. Los demás `tests.py` siguen siendo esqueletos vacíos.

Lo demás son **diagnósticos re-ejecutables**: scripts que verifican contra el mundo real (la red, la base) en vez de contra aserciones. Se corren a mano cuando hace falta, no en cada commit.

## Niveles montados

| Nivel | Estado |
|---|---|
| Unitario / integración (`django.test`, runner nativo) | **Sí** — solo `source` (adjuntos) |
| E2E | No montado |
| Diagnósticos manuales | **Sí** — ver abajo |

Sin `pytest` ni `pytest-django`: el runner nativo alcanza para lo que hay y no agrega dependencia. El resto de [[task-14]] sigue abierto, incluido mudar a la suite el diagnóstico de política de fallos.

## Suite de tests

```bash
DATABASE_SCHEMA= python manage.py test source --noinput
```

Ocho tests, ~0.04 s, **sin red y sin costo**: cubren el invariante de escritura de adjuntos de `source/attachment/` —si algo falla, no queda fila `NoteFile` sin archivo real detrás, y los adjuntos previos solo desaparecen cuando el nuevo ya está escrito—. Seis usan un generador de laboratorio (excepción de red, contenido vacío, `build` que devuelve `None`, storage caído al escribir, camino feliz con `replace=True`, y `replace=False` que ni siquiera descarga); dos ejercitan los generadores reales de Reforma y La Jornada con su llamada de red y su render parcheados con `unittest.mock`.

El `DATABASE_SCHEMA=` del comando es obligatorio en local: el `.env` apunta al schema `ocsa`, que no existe en la base de test recién creada, y sin vaciarlo la corrida muere en `MigrationSchemaMissing`. El storage no se toca: cada test redirige el campo `NoteFile.file` a un directorio temporal.

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

El segundo escribe en `ArticleQualify` con `is_test=True`, **sin tocar** `Article.criteria` ni `certainty_degree`, y es reanudable: salta lo ya calificado con el mismo esquema, así que re-ejecutarlo no vuelve a cobrar. Cada corrida necesita un `ROUND` propio —ancla su `QualifySchema` a un `ScrapedRecord` marcador con fechas de 1900— y acepta `ENGINE` para comparar modelos. Se usó para fijar [[adr-0006]] y [[adr-0007]]; el detalle está en `../docs/records/2026-08-01-criterio-de-opinion-politica.md`.

### Política de fallos del ciclo de clasificación

```bash
python .claude/diagnostics/batch_failure_policy.py
```

**El único diagnóstico que no cuesta nada:** no toca la red ni la cuota de Gemini, y revierte la transacción al terminar. Sustituye `RequestGemini` por un doble que falla a voluntad y comprueba las cuatro conductas que fija [[adr-0010]] — cortacircuitos a los cinco fallos idénticos, recreación del caché con tope de dos, caída a inline reportada una sola vez, y lote que termina completo pese a fallos sueltos — ejercitando el `build_criteria` real, que desde [[task-5]] es la única ruta. Sale con código 1 si algo no cuadra.

### Importación de archivos geográficos

```bash
python .claude/diagnostics/geo_import_check.py
```

**Gratis y sin base:** fabrica en un directorio temporal los archivos que llegan del editor (GeoJSON de dos polígonos, shapefile comprimido en EPSG:6372, KML de una y de dos capas, GeoJSON con tipos mezclados, shapefile sin `.prj`, extensión ajena) y verifica el camino `space_time.geo_import.read_geo_file` → `space_time.geometry.normalize_geojson`: reproyección a EPSG:4326, fusión en Multi\*, conservación de atributos y los mensajes de rechazo en español. Sale con código 1 si algo no cuadra. Es la verificación a correr después de tocar `geo_import.py` o el contrato de `geometry.py`.

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

## Cuidados al ejercitar el pipeline

- **El scraping gasta.** El proxy se cobra por tráfico y PressReader tiene un slot de sesión único; correr diagnósticos en bucle tiene costo real.
- **Los criterios llaman a Gemini.** Cualquier prueba que dispare `build_criteria` en `FirstCriteriaManager` o `PreCaptureManager` consume cuota.
- **La base local (`ocsa-local2`) va desfasada** respecto de producción. Sirve para diagnosticar, no para concluir sobre volúmenes actuales.
