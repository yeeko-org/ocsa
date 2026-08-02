# TESTING

Estado real del repo, no un ideal: **hoy no hay suite de tests montada.** Los `tests.py` de las apps son los esqueletos vacíos que genera `startapp`. `manage.py test` corre y no ejercita nada.

Lo que sí existe son **diagnósticos re-ejecutables**: scripts que verifican contra el mundo real (la red, la base) en vez de contra aserciones. Se corren a mano cuando hace falta, no en cada commit.

## Niveles montados

| Nivel | Estado |
|---|---|
| Unitario (pytest + pytest-django) | No montado |
| Integración | No montado |
| E2E | No montado |
| Diagnósticos manuales | **Sí** — ver abajo |

Montarlos es [[task-14]], que incluye mudar ahí el diagnóstico de política de fallos —hoy el único verificable sin costo— y decidir el runner: el default del stack es `pytest` + `pytest-django`, pero es dependencia nueva. Esta tabla y la sección de comandos se actualizan aquí cuando ocurra.

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

El segundo escribe en `ArticleQualify` con `is_test=True`, **sin tocar** `Article.criteria` ni `certainty_degree`, y es reanudable: salta lo ya calificado con el mismo esquema, así que re-ejecutarlo no vuelve a cobrar. Cada corrida necesita un `ROUND` propio —ancla su `QualifySchema` a un `ScrapedRecord` marcador con fechas de 1900— y acepta `ENGINE` para comparar modelos. Se usó para fijar [[adr-0006]] y [[adr-0007]]; el detalle está en `docs/records/2026-08-01-criterio-de-opinion-politica.md`.

### Política de fallos del ciclo de clasificación

```bash
python .claude/diagnostics/batch_failure_policy.py
```

**El único diagnóstico que no cuesta nada:** no toca la red ni la cuota de Gemini, y revierte la transacción al terminar. Sustituye `RequestGemini` por un doble que falla a voluntad y comprueba las cuatro conductas que fija [[adr-0010]] — cortacircuitos a los cinco fallos idénticos, recreación del caché con tope de dos, caída a inline reportada una sola vez, y lote que termina completo pese a fallos sueltos — ejercitando el `build_criteria` real, que desde [[task-5]] es la única ruta. Sale con código 1 si algo no cuadra.

### Sonda de Proceso

`source/tests.py::probe_proceso_sections()` cuenta secciones y artículos de un issue de PressReader. **Hay que llamarla explícitamente** (shell de Django o import); vive dentro de una función justo para que `manage.py test` no la dispare al importar el módulo. Consume slot de sesión de PressReader.

## Credenciales

Todo lo que los diagnósticos necesitan vive en `.env`: `PROXY_KEY` para el scraping vía proxy, `PRESSREADER_USER`/`PRESSREADER_PASS` para Proceso, `GEMINI_API_KEY` para el pipeline de criterios. No hay credenciales de prueba separadas: los diagnósticos golpean servicios reales.

## Cuidados al ejercitar el pipeline

- **El scraping gasta.** El proxy se cobra por tráfico y PressReader tiene un slot de sesión único; correr diagnósticos en bucle tiene costo real.
- **Los criterios llaman a Gemini.** Cualquier prueba que dispare `build_criteria` en `FirstCriteriaManager` o `PreCaptureManager` consume cuota.
- **La base local (`ocsa-local2`) va desfasada** respecto de producción. Sirve para diagnosticar, no para concluir sobre volúmenes actuales.
