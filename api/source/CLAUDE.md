## Módulo `source/` — Pipeline de notas periodísticas

Gestiona la ingesta de artículos (Jornada, Reforma, Proceso) y su conversión
en notas curadas con menciones estructuradas.

---

## Scraping — gotchas de acceso

**Cloudflare protege a La Jornada con tres controles independientes.** Hay que satisfacer los tres o el 403 es permanente:

1. **Fingerprint TLS** — solo pasa `curl_cffi` con `impersonate="chrome"`; con `requests`/`urllib3` el 403 es inevitable, da igual el User-Agent.
2. **Reputación de IP** — la IP del EC2 (datacenter AWS) recibe 403 en directo, así que `PROXY_KEY` (.env, DataImpulse, sufijo `__cr.mx` = ruta México) es indispensable en producción. Desde IP residencial estorba.
3. **Continuidad de sesión** — Cloudflare evalúa sesiones, no peticiones: sin cookies compartidas ni `Referer` encadenado, cada URL vuelve a caer en el challenge.

`ScraperSession` (`scraper/scraper_base.py`) cubre el tercero: una sesión por lote, creada en `ManagerScraper.__init__` y propagada hasta `ArticleScraper`. `get_content` la recibe como `session=`; sin ella cae a una thread-local. `warmup_url` solo aplica a fuentes servidas como sitio web. Proceso queda fuera de esta ruta: va por `get_json_content` contra PressReader.

🚫 **Nunca metas backoff en los reintentos de 403.** Es un challenge que se resuelve al segundo intento dentro de la misma sesión, no un rate limit que se cure esperando. El `sleep(2**n)` anterior costaba 138 s por día y perdía 6 de 8 secciones; sano son ~3.5 s por día.

Un `407 NO_USER` = credenciales del proxy caducas, no un bug de código.

Diagnóstico: `python source/scraper/scraper_access_test.py [YYYY/MM/DD]`
(modo Jornada) o `... <url> [--proxy] [--xml]` (cualquier otra fuente).

**Los `mapeo` de Reforma vienen a escala corta.** Las fracciones del XML de sección se quedan ~1.9 % por debajo de la mancha real del PDF, en ambos ejes y sin traslación: la arista izquierda cae bien, la derecha y la inferior se quedan cortas. Lo corrige `MAPEO_SCALE` en `source/attachment/pdf_crop.py`. Ahí mismo: un folio puede cargar piezas visualmente disjuntas (el artículo y un recuadro ajeno), y el recorte se queda solo con la componente conexa de mayor área.

---

## Regeneración de adjuntos — gotchas

`python manage.py regenerate_note_files --mode reforma|backfill|all [--ids] [--limit] [--dry-run]` cubre los dos universos de task-42. Se apoya en `source/attachment/generate_attachment()`, así que **exige un `Article` ligado a la nota**: sin él no hay de dónde sacar el folio ni la fecha, y la nota se salta reportando la razón (no se inventa contenido).

**El generador no alcanza a la mayoría del universo de Reforma.** De las notas cuyo único adjunto es el autogenerado-portada, más de la mitad no tiene `Article` — son capturas manuales o notas anteriores al scraping. Esas quedan fuera del alcance del comando por diseño.

**Las que sí tienen `Article` no traen `metadata["paginas"]`**: todas caen en `resolve_page_from_section()`, o sea una descarga del XML de sección por nota. Es la ruta cara y la que hay que presupuestar en la corrida masiva, no la barata.

🚫 `--mode backfill` no toca `Note.pages` (usa `replace=False`, y `update_note_pages` solo corre con `replace=True`). Una nota rellenada queda con su `pages` original —`None` incluido— aunque el adjunto sí traiga código de página.

**`jornada_html.trim_edges` revienta con `IndexError`** cuando el nodo solo contiene espacio en blanco: tras el `lstrip()` de la primera cadena, BeautifulSoup elimina el nodo vacío y el `find_all(string=True)` siguiente devuelve una lista vacía. Reproducible con el artículo `2025/12/15/003n1pol`.

## Ciclo de vida de un artículo

```
ScrapedRecord        ← lote de scraping (fuente + rango de fechas)
  └── Article[]      ← artículo crudo con HTML, párrafos y scoring IA

Article
  ├── criteria / certainty_degree          ← scoring de 1ª pasada (>100 pasa)
  ├── second_criteria / second_certainty_degree ← scoring de 2ª pasada (>100 pasa)
  └── pre_capture                          ← JSON con menciones extraídas por IA

Article → Note                             ← conversión editorial
Note
  ├── pre_mentions    ← copia inicial del JSON de pre_capture
  ├── frozen_pre_capture ← si True, bloquea re-procesamiento
  └── mentions[]      ← menciones confirmadas (una por proyecto en la nota)

Mention (nota × proyecto)
  ├── StatusHistory[]
  ├── Impact[]
  ├── Participant[]  →  Actor
  │     └── Interest[]
  └── Event[]
        └── Involved[]  →  Participant
```

---

## Clasificación con IA — una sola ruta

Los cuatro flujos heredan de `BaseCriteriaManager` (`source/criteria/__init__.py`) y se disparan con `build_criteria()`:

| Subclase | Se dispara desde |
|---|---|
| `FirstCriteriaManager`, `SecondCriteriaManager` | `api/api/views/scraping/views.py` |
| `PreCaptureManager` | vistas de artículo y nota |
| `ReclassifyLegalManager` | `manage.py reclassify_legal_events` |

Dos trampas: `prompt_name`, `version` y `seconds_cache` son atributos de
clase sin default global —una subclase sin `version` revienta al
construirse—, y `first`/`second` emiten el subtítulo sin numerar (`adr-0011`)
porque su esquema acota las referencias a `ge=1` y un `[0]` rompe la
validación. `pdf_import/clean.py` queda fuera del contrato a propósito.

---

## Pre-captura asistida por IA

El proceso lo orquesta `source/criteria/pre_capture.py` (`PreCaptureManager`).
Solo procesa artículos con `second_certainty_degree > 100` y sin `Note` aún.

El prompt usado está en `source/prompts/gemini_pre_capture_criteria_v2.txt`.
Los esquemas Pydantic de validación del JSON de salida están en
`source/base_models.py` (`NoteBase`, `MentionBase`, y subclases).

La hidratación (`save_criteria_results`) convierte textos libres del JSON de
la IA en IDs de Django: estados → `space_time.State`, municipios →
`space_time.Municipality`, tipos de impacto → `impact.ImpactType`, etc.

---

## Scoring de artículos

`Article.sum_degrees()` pondera la presencia de features en párrafos:

| Feature | Peso |
|---------|------|
| opponents | 13 |
| social_impacts | 18 |
| ecological_impacts | 24 |
| acts_of_violence | 21 |
| collective_actions | 20 |

---

## Notas legadas desde PDF

Notas pre-scraping guardadas como PDF (tienen `Note`/`NoteFile` pero no
`Article` con contenido). `source/pdf_import/` las rescata en dos fases
idempotentes: extracción del crudo (PyMuPDF → `Article.html_content`) y
limpieza con Gemini orientada por el título de la `Note`
(→ `Article.paragraphs`). Excluye La Jornada. Disparador:
`python manage.py import_pdf_notes`. Esquema: `PdfCleanResult`.

---

Para definiciones conceptuales de las entidades que genera el pipeline
(proyecto, actor, impacto, evento, etc.), ver el skill `ocs-entities`.