# Insumos geográficos del INEGI

Los catálogos y la cartografía que alimentan `space_time` vienen de dos productos distintos del INEGI. Los archivos pesados no se versionan: se traen con `./download_inegi.sh` (idempotente; `--force` los rehace).

| Archivo | Producto | ¿Versionado? |
|---|---|---|
| `00mun.shp/.dbf/.shx/.prj/.cpg` | Marco Geoestadístico Integrado 2024, capa municipal | No (el .shp pesa ~61 MB) |
| `00a.xml`, `metadato_mgi_2024.txt`, `mg_2024_integrado.txt/.xml` | Metadatos del mismo producto | Sí |
| `localidades.csv` / `.txt` | Catálogo Único de Claves de Áreas Geoestadísticas (AGEEML), nivel localidad | No (~56 MB cada uno) |
| `municipios.csv` / `.txt` | El mismo catálogo AGEEML, nivel municipio | Sí |

**Cuidado con `git add`:** `00mun.shp` y `localidades.*` suman más de 170 MB. No los subas; regenéralos con el script.

## Fuentes

- Marco Geoestadístico Integrado 2024 (ficha `794551132173`, corte agosto 2024): https://www.inegi.org.mx/temas/mg/#descargas
- Catálogo Único de Claves (AGEEML), catálogos nacionales completos: https://www.inegi.org.mx/app/ageeml/

Los ZIP del AGEEML nombran sus miembros con marca de tiempo (`AGEEML_<ts>.csv`), por eso el script los elige por extensión y no por nombre. Se toma la variante ANSI (latin-1), que es la que abren `load_municipios` y `load_localidades`; la variante `_utf8` se descarta.

El corte del AGEEML es irregular y el primer campo cambió de `MAPA` a `CVEGEO` entre cortes. Ninguno de los dos loaders lo usa —leen `CVE_ENT`, `CVE_MUN`, `CVE_LOC`, `NOM_*`, `POB_TOTAL` y, en localidades, `LAT_DECIMAL`, `LON_DECIMAL` y `ALTITUD`—, así que refrescar el catálogo no rompe la carga.

## Carga

```bash
python manage.py load_states_data
python manage.py load_municipios
python manage.py load_localidades
```
