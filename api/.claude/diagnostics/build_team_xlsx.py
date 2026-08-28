"""Arma el XLSX de inconsistencias que se envía al equipo OCSA ([[task-96]]).

Solo lee: cruza los CSV del backfill de geolocalización ([[task-83]]) con la
base local para traducir ids a nombres y para poner el proyecto y el estatus
de cada ubicación, que es lo único que el equipo reconoce a simple vista.

Los pines lejanos y los casos irresolubles no van aquí: esos se marcan en el
dashboard con estatus y comentario, no en un archivo.

    python api/.claude/diagnostics/build_team_xlsx.py
"""
import csv
import os
import re
import sys

import django

BASE = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

from space_time.models import (  # noqa: E402
    Location, Locality, Municipality, State)

CLAUDE_DIR = os.path.join(BASE, ".claude")
VERDICTS_DIR = os.path.join(CLAUDE_DIR, "verdicts")
STAMP = "2026-08-28"
ORPHANS = os.path.join(CLAUDE_DIR, f"dashboard_orphans_{STAMP}.csv")
CHANGES = os.path.join(CLAUDE_DIR, f"geolocate_fill_changes_{STAMP}.csv")
VERDICTS = os.path.join(VERDICTS_DIR, "legacy_names_verdicts.csv")
MANUAL = os.path.join(
    VERDICTS_DIR, "legacy_names_manual_project.csv")
YEEKO = os.path.join(VERDICTS_DIR, "yeeko_states_verdicts.csv")
OUT = os.path.join(CLAUDE_DIR, f"aviso_equipo_{STAMP}.xlsx")

# Ubicaciones cuyo padre se perdió en la migración: el origen no está en
# ninguna tabla, se reconstruyó a mano desde las notas del sistema anterior.
LOST_LINK = {
    7280: "acción colectiva sin forma en el sistema anterior; ver nota 38",
    7993: "acción colectiva sin forma en el sistema anterior; ver nota 133",
    8091: "acción colectiva sin forma en el sistema anterior; ver nota 1014",
    9407: "afectación sin nota en el sistema anterior",
    10604: "afectación sin nota en el sistema anterior",
}

FIELD_ES = {
    "state": "estado",
    "municipality": "municipio",
    "locality": "localidad",
    "municipalities": "municipios atravesados",
    "centroide": "centroide",
}


def read_csv(path, encoding="utf-8-sig"):
    with open(path, encoding=encoding, newline="") as handle:
        return list(csv.DictReader(handle))


# --- caché de la base -------------------------------------------------

STATES = {s.id: s.name for s in State.objects.all()}
MUNIS = {
    m.id: (m.name, STATES.get(m.state_id, ""))
    for m in Municipality.objects.all()
}
LOCALITIES = {loc.id: loc.name for loc in Locality.objects.all()}


class LocInfo:
    """Lo que el equipo necesita ver de una ubicación, ya resuelto."""

    def __init__(self, loc):
        self.id = loc.id
        self.details = (loc.details or "").strip()
        self.state = loc.state.name if loc.state else ""
        self.municipality = loc.municipality.name if loc.municipality else ""
        self.locality = loc.locality.name if loc.locality else ""
        self.status = (loc.status_location.public_name
                       if loc.status_location else "")
        if loc.project_id:
            self.parent = "proyecto"
            self.project_id = loc.project_id
            self.project = loc.project.name
        elif loc.event_id:
            self.parent = "evento"
            self.project_id = loc.event.mention.project_id
            self.project = loc.event.mention.project.name
        elif loc.impact_id:
            self.parent = "impacto"
            self.project_id = loc.impact.mention.project_id
            self.project = loc.impact.mention.project.name
        else:
            self.parent = "ninguno"
            self.project_id = ""
            self.project = ""


def load_locations():
    qs = Location.objects.select_related(
        "state", "municipality", "locality", "status_location", "project",
        "event__mention__project", "impact__mention__project")
    return {loc.id: LocInfo(loc) for loc in qs}


LOCS = load_locations()
MISSING = set()


def info(location_id):
    loc = LOCS.get(int(location_id))
    if loc is None:
        MISSING.add(int(location_id))
    return loc


# --- traducción de valores del CSV de cambios -------------------------

def muni_label(muni_id, with_state=False):
    name, state = MUNIS.get(int(muni_id), ("", ""))
    if not name:
        return f"(municipio {muni_id})"
    return f"{name} ({state})" if with_state else name


def value_label(field, raw):
    if not raw:
        return ""
    if field == "state":
        return STATES.get(int(raw), f"(estado {raw})")
    if field == "municipality":
        return muni_label(raw)
    if field == "locality":
        return LOCALITIES.get(int(raw), f"(localidad {raw})")
    if field == "municipalities":
        return "; ".join(
            muni_label(part.strip(), with_state=True)
            for part in raw.split(";") if part.strip())
    return raw


# --- nombres del sistema anterior -------------------------------------

TEMPLATE_FIELD = {
    "municipio": "municipality",
    "localidad": "locality",
    "homonimo": "locality",
}
YEEKO_PATTERNS = {
    "state": r"Estado no encontrado:\s*([^;]+)",
    "municipality": r"Municipio no encontrado:\s*([^;]+)",
    "locality": r"Localidad no encontrada:\s*([^;]+)",
}


def build_legacy_index():
    """(location_id, campo) -> nombre tal como venía del sistema anterior."""
    index = {}
    for row in read_csv(VERDICTS):
        field = TEMPLATE_FIELD.get(row["template"])
        if field:
            index.setdefault(
                (int(row["location_id"]), field), row["legacy_value"])
    for row in read_csv(MANUAL):
        for field in ("municipality", "locality"):
            index.setdefault(
                (int(row["location_id"]), field), row["legacy_value"])
    for row in read_csv(YEEKO):
        comment = row.get("comment_verbatim", "")
        for field, pattern in YEEKO_PATTERNS.items():
            found = re.search(pattern, comment)
            if found:
                index.setdefault(
                    (int(row["location_id"]), field), found.group(1).strip())
    return index


LEGACY = build_legacy_index()

VACIAR = {
    int(row["location_id"]): row
    for row in read_csv(VERDICTS) if row["verdict"] == "vaciar"
}


# --- hojas ------------------------------------------------------------

def sheet_orphans():
    headers = ["id_ubicacion", "id_proyecto", "proyecto", "detalle",
               "estado", "municipio", "estatus", "origen"]
    rows = []
    for row in read_csv(ORPHANS):
        if row["decision"] != "listar":
            continue
        loc = info(row["location_id"])
        rows.append([
            int(row["location_id"]), "", "",
            row["details"], row["state"], row["municipality"],
            loc.status if loc else "", ""])
    for location_id, origin in LOST_LINK.items():
        loc = info(location_id)
        rows.append([
            location_id, "", "",
            loc.details if loc else "",
            loc.state if loc else "",
            loc.municipality if loc else "",
            loc.status if loc else "", origin])
    return headers, rows


def appended_text(before, after):
    """Lo que el backfill agregó a `details`, sin repetir lo ya capturado."""
    if before and after.startswith(before):
        return after[len(before):].lstrip("\n")
    return after


def sheet_details(changes):
    headers = ["id_ubicacion", "id_proyecto", "proyecto", "padre",
               "texto_agregado", "estado", "municipio", "localidad",
               "estatus"]
    rows = []
    for row in changes:
        if row["field"] != "details":
            continue
        loc = info(row["location_id"])
        rows.append([
            int(row["location_id"]),
            loc.project_id if loc else "", loc.project if loc else "",
            loc.parent if loc else "",
            appended_text(row["before"], row["after"]),
            loc.state if loc else "", loc.municipality if loc else "",
            loc.locality if loc else "", loc.status if loc else ""])
    return headers, rows


def sheet_emptied(changes):
    headers = ["id_ubicacion", "id_proyecto", "proyecto", "nombre_anterior",
               "municipio_actual", "tiene_geometria", "candidatos_homonimos",
               "estatus"]
    rows = []
    for row in changes:
        if row["field"] != "locality" or row["after"]:
            continue
        location_id = int(row["location_id"])
        loc = info(location_id)
        verdict = VACIAR.get(location_id, {})
        candidates = verdict.get("candidate_id", "")
        rows.append([
            location_id,
            loc.project_id if loc else "", loc.project if loc else "",
            verdict.get("legacy_value", ""),
            loc.municipality if loc else "",
            "sí" if verdict.get("has_geometry") == "1" else "no",
            len(candidates.split("|")) if candidates else "",
            loc.status if loc else ""])
    return headers, rows


def sheet_engine(changes):
    headers = ["id_ubicacion", "id_proyecto", "proyecto", "campo", "antes",
               "despues", "estatus"]
    coords = {}
    rows = []
    for row in changes:
        if row["source"] != "engine":
            continue
        location_id = int(row["location_id"])
        field = row["field"]
        if field in ("latitude", "longitude"):
            coords.setdefault(location_id, {})[field] = (
                row["before"], row["after"])
            continue
        loc = info(location_id)
        rows.append([
            location_id,
            loc.project_id if loc else "", loc.project if loc else "",
            FIELD_ES[field],
            value_label(field, row["before"]),
            value_label(field, row["after"]),
            loc.status if loc else ""])

    def pair(values, index):
        lat = values.get("latitude", ("", ""))[index]
        lon = values.get("longitude", ("", ""))[index]
        return f"{lat}, {lon}" if lat or lon else ""

    for location_id, values in coords.items():
        loc = info(location_id)
        rows.append([
            location_id,
            loc.project_id if loc else "", loc.project if loc else "",
            "centroide", pair(values, 0), pair(values, 1),
            loc.status if loc else ""])
    rows.sort(key=lambda row: (row[0], row[3]))
    return headers, rows


# El dictamen de estados yeeko no guarda el nombre legado por campo: ahí
# la fila queda sin `nombre_anterior` y decirlo evita leerla como un
# llenado sin origen.
DEDUCED = "deducido del comentario"


def sheet_by_name(changes):
    headers = ["id_ubicacion", "id_proyecto", "proyecto", "campo",
               "nombre_anterior", "valor_asignado", "estatus"]
    rows = []
    for row in changes:
        field = row["field"]
        if row["source"] == "engine" or field not in FIELD_ES:
            continue
        if field == "municipalities" or not row["after"]:
            continue
        location_id = int(row["location_id"])
        loc = info(location_id)
        rows.append([
            location_id,
            loc.project_id if loc else "", loc.project if loc else "",
            FIELD_ES[field],
            LEGACY.get((location_id, field)) or DEDUCED,
            value_label(field, row["after"]),
            loc.status if loc else ""])
    return headers, rows


# --- escritura --------------------------------------------------------

README = [
    ("Ubicaciones sueltas",
     "Ubicaciones que no cuelgan de ningún proyecto, evento o afectación: "
     "quedaron sin padre en la migración del sistema anterior. Las primeras "
     "traen el dato que se capturó en su momento; las cinco últimas llevan "
     "en «origen» la pista con la que se reconstruyó de dónde venían. Lo "
     "que necesitamos de ustedes: decir a qué proyecto o nota pertenece "
     "cada una, o si se pueden borrar. A partir del [fecha del deploy] el "
     "dashboard ya no permite crear ubicaciones sueltas."),
    ("Nombres a detalles",
     "Nombres de lugar que el sistema anterior guardaba como si fueran "
     "localidades del INEGI pero no lo son (colonias, ejidos, barrios, "
     "parajes, referencias de calle). No se perdió nada: el texto pasó al "
     "campo «detalles» de la ubicación, y ahí sigue visible y editable. La "
     "columna «texto_agregado» es exactamente lo que se agregó. Revisen "
     "que el texto quedó donde tiene sentido; si alguno sí correspondía a "
     "una localidad real, corríjanlo en el dashboard."),
    ("Localidades vaciadas",
     "Localidades que la migración llenó a ciegas: el nombre capturado "
     "existe en dos o más localidades del mismo municipio y el sistema "
     "eligió una al azar. Como no hay manera de saber cuál era, se dejó el "
     "campo de localidad vacío y se conserva el nombre anterior en esta "
     "lista. Lo que necesitamos de ustedes: elegir la localidad correcta "
     "en el dashboard, o dejarla vacía si el municipio alcanza."),
    ("Llenado automático",
     "Datos que el motor de geolocalización dedujo del trazo o del pin de "
     "cada ubicación a partir de la cartografía del INEGI, en el backfill "
     "del [fecha del deploy]. «Municipios atravesados» es un campo nuevo: "
     "lo calcula el sistema al guardar y no se captura a mano. Es "
     "informativo; no hace falta hacer nada, salvo avisar si alguno se ve "
     "claramente mal."),
    ("Llenado por nombre",
     "Estados, municipios y localidades que estaban vacíos y se llenaron "
     "cruzando el nombre que traía el sistema anterior con el catálogo del "
     "INEGI. La columna «nombre_anterior» es lo que decía el registro "
     "viejo y «valor_asignado» es el catálogo que se le puso; "
     "«deducido del comentario» marca las filas donde el nombre no "
     "venía en un campo sino en el comentario de la ubicación. Es "
     "informativo; revísenlo por muestreo y avisen si algún nombre "
     "quedó mal emparejado."),
]

MAX_WIDTH = 60
HEADER_FILL = PatternFill("solid", fgColor="DDDDDD")


def write_sheet(book, title, headers, rows):
    sheet = book.create_sheet(title)
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    sheet.freeze_panes = "A2"
    for index, _ in enumerate(headers, start=1):
        letter = get_column_letter(index)
        longest = max(
            [len(str(headers[index - 1]))]
            + [len(str(row[index - 1])) for row in rows] or [0])
        sheet.column_dimensions[letter].width = min(longest + 2, MAX_WIDTH)
        for cell in sheet[letter][1:]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    return sheet


def write_readme(book, counts):
    sheet = book.create_sheet("Léeme", 0)
    sheet["A1"] = "Ubicaciones que necesitan su revisión — OCSA"
    sheet["A1"].font = Font(bold=True, size=14)
    sheet["A2"] = (
        "Este archivo acompaña los cambios de geolocalización que entraron "
        "el [fecha del deploy]. Cada hoja es una lista distinta; abajo se "
        "explica qué trae cada una y qué hay que hacer con ella. Los "
        "pines que caen lejos de lo capturado y los casos que no se "
        "pudieron resolver no vienen aquí: quedaron marcados en el "
        "dashboard con su estatus y un comentario.")
    sheet["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    sheet.row_dimensions[2].height = 60
    row_index = 4
    for title, text in README:
        sheet.cell(row=row_index, column=1, value=title).font = Font(bold=True)
        sheet.cell(row=row_index, column=2,
                   value=f"{counts.get(title, 0)} filas")
        cell = sheet.cell(row=row_index + 1, column=1, value=text)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        sheet.merge_cells(
            start_row=row_index + 1, start_column=1,
            end_row=row_index + 1, end_column=6)
        sheet.row_dimensions[row_index + 1].height = 75
        row_index += 3
    sheet.column_dimensions["A"].width = 30
    for letter in "BCDEF":
        sheet.column_dimensions[letter].width = 20
    sheet.freeze_panes = "A2"


def main():
    changes = read_csv(CHANGES)
    sheets = [
        ("Ubicaciones sueltas", sheet_orphans()),
        ("Nombres a detalles", sheet_details(changes)),
        ("Localidades vaciadas", sheet_emptied(changes)),
        ("Llenado automático", sheet_engine(changes)),
        ("Llenado por nombre", sheet_by_name(changes)),
    ]
    book = Workbook()
    book.remove(book.active)
    counts = {}
    for title, (headers, rows) in sheets:
        write_sheet(book, title, headers, rows)
        counts[title] = len(rows)
    write_readme(book, counts)
    book.save(OUT)
    for title, count in counts.items():
        print(f"{title}: {count}")
    if MISSING:
        print(f"ubicaciones no encontradas en la base: {sorted(MISSING)}")
    print(f"escrito: {OUT}")


if __name__ == "__main__":
    main()
