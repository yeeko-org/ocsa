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

Cuando se monte el primer nivel, el default para este stack es `pytest` + `pytest-django`, y esta tabla y la sección de comandos se actualizan aquí.

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

### Sonda de Proceso

`source/tests.py::probe_proceso_sections()` cuenta secciones y artículos de un issue de PressReader. **Hay que llamarla explícitamente** (shell de Django o import); vive dentro de una función justo para que `manage.py test` no la dispare al importar el módulo. Consume slot de sesión de PressReader.

## Credenciales

Todo lo que los diagnósticos necesitan vive en `.env`: `PROXY_KEY` para el scraping vía proxy, `PRESSREADER_USER`/`PRESSREADER_PASS` para Proceso, `GEMINI_API_KEY` para el pipeline de criterios. No hay credenciales de prueba separadas: los diagnósticos golpean servicios reales.

## Cuidados al ejercitar el pipeline

- **El scraping gasta.** El proxy se cobra por tráfico y PressReader tiene un slot de sesión único; correr diagnósticos en bucle tiene costo real.
- **Los criterios llaman a Gemini.** Cualquier prueba que dispare `build_first_criteria` o `pre_capture` consume cuota.
- **La base local (`ocsa-local2`) va desfasada** respecto de producción. Sirve para diagnosticar, no para concluir sobre volúmenes actuales.
