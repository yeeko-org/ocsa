# Insumos geográficos del INEGI

Los catálogos y la cartografía que alimentan `space_time` vienen de dos productos distintos del INEGI. Los archivos pesados no se versionan: se traen con `./download_inegi.sh` (idempotente; `--force` los rehace, y `--force mgi|localidades|municipios` rehace solo ese producto —refrescar el catálogo de localidades no obliga a rebajar los 271 MB del Marco Geoestadístico—).

| Archivo | Producto | ¿Versionado? |
|---|---|---|
| `00ent.shp/.dbf/.shx/.prj/.cpg` | Marco Geoestadístico Integrado 2024, capa estatal | No (el .shp pesa ~14 MB) |
| `00mun.shp/.dbf/.shx/.prj/.cpg` | Marco Geoestadístico Integrado 2024, capa municipal | No (el .shp pesa ~61 MB) |
| `00l.shp/.dbf/.shx/.prj/.cpg` | Marco Geoestadístico Integrado 2024, localidades amanzanadas (51,279 polígonos: 4,904 urbanas y 46,375 rurales) | No (el .shp pesa ~87 MB) |
| `00a.xml`, `metadato_mgi_2024.txt`, `mg_2024_integrado.txt/.xml` | Metadatos del mismo producto | Sí |
| `localidades.csv` / `.txt` | Catálogo Único de Claves de Áreas Geoestadísticas (AGEEML), nivel localidad | No (~56 MB cada uno) |
| `municipios.csv` | El mismo catálogo AGEEML, nivel municipio | Sí |

**Cuidado con `git add`:** `00ent.shp`, `00mun.shp`, `00l.shp` y `localidades.*` suman más de 270 MB. No los subas; regenéralos con el script.

Las tres capas del Marco Geoestadístico vienen del mismo zip (~271 MB), que el script no conserva: si falta cualquiera de las tres, lo vuelve a bajar y extrae solo la que falte. El zip trae también `00lpr.*` (localidades rurales como puntos), que no se usa: el motor de geolocalización solo consume polígonos.

## Fuentes

- Marco Geoestadístico Integrado 2024 (ficha `794551132173`, corte agosto 2024): https://www.inegi.org.mx/temas/mg/#descargas
- Catálogo Único de Claves (AGEEML), catálogos nacionales completos: https://www.inegi.org.mx/app/ageeml/

Los ZIP del AGEEML nombran sus miembros con marca de tiempo (`AGEEML_<ts>.csv`), por eso el script los elige por extensión y no por nombre. Se toma la variante ANSI (latin-1), que es la que abren `load_municipios` y `load_localidades`; la variante `_utf8` se descarta.

El corte del AGEEML es irregular y el primer campo cambió de `MAPA` a `CVEGEO` entre cortes. Ninguno de los dos loaders lo usa —leen `CVE_ENT`, `CVE_MUN`, `CVE_LOC`, `NOM_*`, `POB_TOTAL`, `AMBITO` y, en localidades, `LAT_DECIMAL`, `LON_DECIMAL` y `ALTITUD`—, así que refrescar el catálogo no rompe la carga. Un corte nuevo suele traer altas y bajas a la vez: `load_localidades` da de alta las nuevas y marca `is_current=False` las que desaparecieron, sin borrar nunca (hay ubicaciones capturadas que apuntan a ellas).

## Carga

```bash
python manage.py load_states_data
python manage.py load_municipios
python manage.py load_localidades
python manage.py load_geometries
```

Los tres últimos son idempotentes y aceptan `--dry-run`: re-correrlos actualiza lo que cambió y crea lo que falte, sin duplicar. `load_geometries` lee `00ent.shp`, `00mun.shp` y `00l.shp`, simplifica los polígonos (50 m estados, 20 m municipios, 10 m localidades; `--simplify` lo cambia) y los guarda como WKB en EPSG:6372 (el CRS nativo del INEGI, en metros) en `StateGeometry`, `MunicipalityGeometry` y `LocalityGeometry` (~45 MB en total); es el insumo del motor de geolocalización `space_time/geolocate.py`. Con `--layer state|municipality|locality` se carga una sola capa.
