#!/usr/bin/env bash
# Descarga los insumos del INEGI que no se versionan por peso:
#   00ent.*                    Marco Geoestadístico Integrado 2024 (estatal)
#   00mun.*                    Marco Geoestadístico Integrado 2024 (municipal)
#   00l.*                      Marco Geoestadístico 2024, localidades amanzanadas
#   localidades.csv / .txt     Catálogo Único de Claves (AGEEML), localidades
#
# Los dos productos se actualizan con cortes irregulares; el script siempre
# trae el vigente. Requiere curl y unzip. Descarga ~375 MB temporales.
#
# Uso: ./download_inegi.sh [--force [mgi|localidades|municipios]]
# Sin producto, --force rehace los tres; con producto, solo ese (refrescar
# el catálogo de localidades no obliga a rebajar los 271 MB del Marco).
set -euo pipefail

DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FORCE=0
FORCE_ONLY=""
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
  FORCE_ONLY="${2:-}"
  case "$FORCE_ONLY" in
    ""|mgi|localidades|municipios) ;;
    *)
      echo "--force acepta mgi, localidades o municipios (no '$FORCE_ONLY')" >&2
      exit 1
      ;;
  esac
fi

MGI_URL="https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/794551132173/mg_2024_integrado.zip"
LOC_URL="https://www.inegi.org.mx/contenidos/app/ageeml/catun_localidad.zip"
# Municipios sí están versionados; se refrescan solo con --force.
MUN_URL="https://www.inegi.org.mx/contenidos/app/ageeml/catun_municipio.zip"

# have <producto> <archivo>: el archivo ya sirve y no se está forzando
# ese producto.
have() {
  [[ -f "$DEST/$2" ]] || return 1
  [[ $FORCE -eq 1 && ( -z "$FORCE_ONLY" || "$FORCE_ONLY" == "$1" ) ]] \
    && return 1
  return 0
}

fetch() {  # fetch <url> <archivo destino en $TMP>
  echo "→ descargando $2"
  curl -fSL --retry 3 --retry-delay 5 -o "$TMP/$2" "$1"
}

# --- Marco Geoestadístico Integrado 2024: estados, municipios, localidades --
# El zip no se conserva, así que basta con que falte una de las capas para
# volver a bajarlo; una vez en disco se extrae solo lo que falta. El patrón
# `00l.*` no alcanza a `00lpr.*` (localidades rurales puntuales), que no se
# usa: el motor solo necesita polígonos.
if have mgi 00ent.shp && have mgi 00mun.shp && have mgi 00l.shp; then
  echo "= 00ent.*, 00mun.* y 00l.* ya están; --force para rehacerlos"
else
  fetch "$MGI_URL" mgi.zip
  for layer in 00ent 00mun 00l; do
    have mgi "$layer.shp" || unzip -o -j -q \
      "$TMP/mgi.zip" "conjunto_de_datos/$layer.*" -d "$DEST"
  done
  # Los metadatos sí están versionados: se extraen solo si faltan.
  for f in metadatos/metadato_mgi_2024.txt metadatos/mg_2024_integrado.txt \
           metadatos/mg_2024_integrado.xml conjunto_de_datos/00a.xml; do
    have mgi "$(basename "$f")" \
      || unzip -o -j -q "$TMP/mgi.zip" "$f" -d "$DEST"
  done
fi

# --- AGEEML: catálogo de localidades ---------------------------------------
# Los miembros del zip llevan marca de tiempo en el nombre (AGEEML_<ts>.csv),
# así que se eligen por extensión, no por nombre. Se toma la variante ANSI
# (latin-1), que es la que esperan los management commands.
extract_ageeml() {  # extract_ageeml <zip> <ext> <destino>
  local member
  member=$(unzip -Z1 "$TMP/$1" "*.$2" | grep -v '_utf8' | head -1)
  [[ -n "$member" ]] || { echo "No hay .$2 en $1" >&2; exit 1; }
  unzip -p "$TMP/$1" "$member" > "$DEST/$3"
  echo "  $member → $3"
}

if have localidades localidades.csv && have localidades localidades.txt; then
  echo "= localidades.* ya están; --force para rehacerlas"
else
  fetch "$LOC_URL" catun_localidad.zip
  extract_ageeml catun_localidad.zip csv localidades.csv
  extract_ageeml catun_localidad.zip txt localidades.txt
fi

# --- AGEEML: catálogo de municipios (versionado) ---------------------------
if have municipios municipios.csv; then
  echo "= municipios.csv ya está; --force para rehacerlo"
else
  fetch "$MUN_URL" catun_municipio.zip
  extract_ageeml catun_municipio.zip csv municipios.csv
fi

echo "Listo. Carga: python manage.py load_municipios \
&& python manage.py load_localidades && python manage.py load_geometries"
