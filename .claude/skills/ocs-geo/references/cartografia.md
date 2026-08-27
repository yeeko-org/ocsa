# Cartografía e insumos geográficos del INEGI

Los catálogos y la cartografía que alimentan `space_time` vienen de dos productos distintos del INEGI y viven en `api/space_time/geo_files/`. Los archivos pesados no se versionan: los trae `api/space_time/geo_files/download_inegi.sh`.

## Fuentes

- **Marco Geoestadístico Integrado 2024** (ficha `794551132173`, corte agosto 2024): https://www.inegi.org.mx/temas/mg/#descargas — la cartografía (polígonos).
- **Catálogo Único de Claves de Áreas Geoestadísticas (AGEEML)**, catálogos nacionales completos: https://www.inegi.org.mx/app/ageeml/ — los catálogos de municipios y localidades, con población, ámbito y coordenadas.

## Archivos

| Archivo | Producto | ¿Versionado? |
|---|---|---|
| `00ent.shp/.dbf/.shx/.prj/.cpg` | Marco Geoestadístico, capa estatal | No (el `.shp` pesa ~14 MB) |
| `00mun.shp/…` | Marco Geoestadístico, capa municipal | No (~61 MB) |
| `00l.shp/…` | Marco Geoestadístico, localidades amanzanadas (51 279 polígonos: 4 904 urbanas y 46 375 rurales) | No (~87 MB) |
| `00a.xml`, `metadato_mgi_2024.txt`, `mg_2024_integrado.txt/.xml` | Metadatos del mismo producto | Sí |
| `localidades.csv` / `.txt` | AGEEML, nivel localidad | No (~56 MB cada uno) |
| `municipios.csv` | AGEEML, nivel municipio | Sí |

**Cuidado con `git add`:** `00ent.shp`, `00mun.shp`, `00l.shp` y `localidades.*` suman más de 270 MB. No subirlos; se regeneran con el script.

`00l` es **un polígono por localidad, urbana o rural** —no solo manchas urbanas—: es lo que hace viable resolver la localidad de un punto por point-in-polygon. El mismo zip trae `00lpr.*` (localidades rurales como puntos), que **no se usa**: el motor solo consume polígonos, y las localidades sin polígono se resuelven por el punto del catálogo AGEEML.

## Descarga

`download_inegi.sh` es idempotente; `--force` rehace todo y `--force mgi|localidades|municipios` rehace solo ese producto —refrescar el catálogo de localidades no obliga a rebajar los 271 MB del Marco Geoestadístico—. Las tres capas del Marco vienen del mismo zip, que el script no conserva: si falta cualquiera de las tres, lo vuelve a bajar y extrae solo la que falte.

**Gotcha de codificación:** los ZIP del AGEEML nombran sus miembros con marca de tiempo (`AGEEML_<ts>.csv`), por eso el script los elige por extensión y no por nombre. Se toma la variante **ANSI (latin-1)**, que es la que abren `load_municipios` y `load_localidades`; la variante `_utf8` se descarta. En los shapefiles, cuando el `.cpg` está presente **no se fuerza codificación**: GDAL la respeta y forzar UTF-8 rompe los acentos.

**Gotcha del corte AGEEML:** el corte es irregular y el primer campo cambió de `MAPA` a `CVEGEO` entre cortes. Ninguno de los dos loaders lo usa —leen `CVE_ENT`, `CVE_MUN`, `CVE_LOC`, `NOM_*`, `POB_TOTAL`, `AMBITO` y, en localidades, `LAT_DECIMAL`, `LON_DECIMAL` y `ALTITUD`—, así que refrescar el catálogo no rompe la carga.

## Modelos y tolerancias

Sin PostGIS. Los polígonos viven en modelos **1:1** con su entidad —`StateGeometry`, `MunicipalityGeometry`, `LocalityGeometry`— como **WKB en EPSG:6372** (~45 MB en total). La separación es deliberada: así los serializers `__all__` de `State` y `Municipality` nunca arrastran la geometría.

`load_geometries` simplifica cada capa con una tolerancia distinta, `--simplify` la cambia y `--layer state|municipality|locality` carga una sola:

| Capa | Fuente | Tolerancia |
|---|---|---|
| estatal | `00ent.shp` | 50 m |
| municipal | `00mun.shp` | 20 m |
| localidad | `00l.shp` | 10 m |

Criterio de los tres valores, medido sobre el Marco 2024: por debajo de esa tolerancia **ningún polígono de la capa pierde más de 1 % de área**.

El shapefile se lee con `pyogrio.raw`; `read_dataframe` exigiría geopandas, que el proyecto no instala.

## Carga

```bash
python manage.py load_states_data
python manage.py load_municipios
python manage.py load_localidades
python manage.py load_geometries
```

Ese es el orden: la geometría cuelga de entidades que los catálogos deben haber creado antes. Los tres últimos son idempotentes y aceptan `--dry-run`: re-correrlos actualiza lo que cambió y crea lo que falte, sin duplicar.

**Ningún loader borra.** Un corte nuevo del AGEEML suele traer altas y bajas a la vez: `load_localidades` da de alta las nuevas y marca `is_current=False` las que desaparecieron, sin borrar jamás —hay ubicaciones capturadas que apuntan a ellas—. El motor solo considera `is_current=True` al buscar localidad por cercanía, pero una ubicación puede seguir mostrando una localidad retirada.

Después de recargar la cartografía hay que reiniciar el proceso: los índices del motor se cachean y no se invalidan (ver [motor.md](motor.md)).
