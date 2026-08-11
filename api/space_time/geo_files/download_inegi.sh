#!/usr/bin/env bash
# Descarga los insumos del INEGI que no se versionan por peso:
#   00mun.*                    Marco Geoestadístico Integrado 2024 (municipal)
#   localidades.csv / .txt     Catálogo Único de Claves (AGEEML), localidades
#
# Los dos productos se actualizan con cortes irregulares; el script siempre
# trae el vigente. Requiere curl y unzip. Descarga ~375 MB temporales.
set -euo pipefail

DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

MGI_URL="https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/794551132173/mg_2024_integrado.zip"
LOC_URL="https://www.inegi.org.mx/contenidos/app/ageeml/catun_localidad.zip"
# Municipios sí están versionados; se refrescan solo con --force.
MUN_URL="https://www.inegi.org.mx/contenidos/app/ageeml/catun_municipio.zip"

have() { [[ $FORCE -eq 0 && -f "$DEST/$1" ]]; }

fetch() {  # fetch <url> <archivo destino en $TMP>
  echo "→ descargando $2"
  curl -fSL --retry 3 --retry-delay 5 -o "$TMP/$2" "$1"
}

# --- Marco Geoestadístico Integrado 2024: capa municipal -------------------
if have 00mun.shp; then
  echo "= 00mun.* ya está; --force para rehacerlo"
else
  fetch "$MGI_URL" mgi.zip
  unzip -o -j -q "$TMP/mgi.zip" 'conjunto_de_datos/00mun.*' -d "$DEST"
  # Los metadatos sí están versionados: se extraen solo si faltan.
  for f in metadatos/metadato_mgi_2024.txt metadatos/mg_2024_integrado.txt \
           metadatos/mg_2024_integrado.xml conjunto_de_datos/00a.xml; do
    have "$(basename "$f")" || unzip -o -j -q "$TMP/mgi.zip" "$f" -d "$DEST"
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

if have localidades.csv && have localidades.txt; then
  echo "= localidades.* ya están; --force para rehacerlas"
else
  fetch "$LOC_URL" catun_localidad.zip
  extract_ageeml catun_localidad.zip csv localidades.csv
  extract_ageeml catun_localidad.zip txt localidades.txt
fi

# --- AGEEML: catálogo de municipios (versionado) ---------------------------
if have municipios.csv; then
  echo "= municipios.* ya están; --force para rehacerlos"
else
  fetch "$MUN_URL" catun_municipio.zip
  extract_ageeml catun_municipio.zip csv municipios.csv
  extract_ageeml catun_municipio.zip txt municipios.txt
fi

echo "Listo. Carga: python manage.py load_municipios && python manage.py load_localidades"
