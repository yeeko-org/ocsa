## Módulo `source/` — Pipeline de notas periodísticas

Gestiona la ingesta de artículos (Jornada, Reforma, Proceso) y su conversión
en notas curadas con menciones estructuradas.

---

## Scraping — gotchas de acceso

**La Jornada está detrás de Cloudflare con *challenge* por fingerprint
TLS.** `requests`/`urllib3` recibe siempre 403 ("Just a moment...",
header `cf-mitigated: challenge`) sin importar User-Agent ni IP. El helper
central `get_content` (`scraper/scraper_base.py`) debe acceder con
`curl_cffi` e `impersonate="chrome"`; pasa con o sin proxy.

El proxy `PROXY_KEY` (.env, DataImpulse, sufijo `__cr.mx` = ruta México)
**no evade Cloudflare**, solo aporta rotación de IP para volumen. Un `407
NO_USER` = credenciales rechazadas (password caduco), no un bug de código.

Diagnóstico: `python source/scraper/scraper_access_test.py [YYYY/MM/DD]`
(modo Jornada) o `... <url> [--proxy] [--xml]` (cualquier otra fuente).

---

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
`source/scraper/examples_pdf_import.py`. Esquema: `PdfCleanResult`.

---

Para definiciones conceptuales de las entidades que genera el pipeline
(proyecto, actor, impacto, evento, etc.), ver el skill `ocs-entities`.