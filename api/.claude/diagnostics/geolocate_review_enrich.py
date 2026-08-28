"""Enriquece la revisión de geolocalización: CSV en español + JSONL crudo.

Solo lectura. Recorre el mismo universo que `geolocate_locations --review`
(ubicaciones con proyecto y con geometría), recalcula la resolución y
agrega población, ámbito y distancias de la localidad capturada y de la
calculada, para que la revisión a mano pueda juzgar cada fila.

    python .claude/diagnostics/geolocate_review_enrich.py
"""

import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402

django.setup()

from space_time.geolocate import (  # noqa: E402
    _locality_points, point_in_meters, resolve_geometry, resolve_point)
from space_time.backfill import (  # noqa: E402
    COMPARED_FIELDS, computed_value, located)

OUT_CSV = Path(".claude/geolocate_review_analizado.csv")
OUT_JSONL = Path(".claude/geolocate_review_raw.jsonl")
OUT_TALLY = Path(".claude/geolocate_review_tally.json")
AGEEML_CSV = Path("space_time/geo_files/localidades.csv")


def ambito_by_code() -> dict:
    """`complete_code` → «U»/«R» del AGEEML.

    `Locality.is_rural` no lo llena ningún loader (está en False para las
    299,568 filas), así que el ámbito se lee del catálogo en disco, que
    es de donde salió la base.
    """
    mapping = {}
    with AGEEML_CSV.open(newline="", encoding="latin1") as handle:
        for row in csv.DictReader(handle):
            code = (f"{row['CVE_ENT']}-{row['CVE_MUN']}-{row['CVE_LOC']}")
            mapping[code] = (row.get("AMBITO") or "").strip().upper()
    return mapping


AMBITO = ambito_by_code()

FIELD_LABEL = {
    "state": "entidad",
    "municipality": "municipio",
    "locality": "localidad",
}
COLUMN = {
    "state": ("entidad_capturada", "entidad_calculada"),
    "municipality": ("municipio_capturado", "municipio_calculado"),
    "locality": ("localidad_capturada", "localidad_calculada"),
}
HEADERS = [
    "id", "proyecto_id", "proyecto", "tipo", "diferencias",
    "localidad_capturada_vacia",
    "entidad_capturada", "entidad_calculada",
    "municipio_capturado", "municipio_calculado",
    "localidad_capturada", "localidad_calculada",
    "pob_localidad_capturada", "pob_localidad_calculada",
    "urbana_capturada", "urbana_calculada",
    "dist_m_localidad_capturada", "dist_m_localidad_calculada",
    "municipios_atravesados",
]


def reference_point(location, resolution):
    """`(lat, lon)` desde el que se miden las distancias."""
    if location.type_location == "point":
        if location.latitude is None or location.longitude is None:
            return None
        return location.latitude, location.longitude
    return getattr(resolution, "centroid", None)


def distance_m(reference, locality):
    if reference is None or locality is None:
        return None
    if locality.latitude is None or locality.longitude is None:
        return None
    origin = point_in_meters(*reference)
    target = point_in_meters(locality.latitude, locality.longitude)
    return round(origin.distance(target), 1)


def locality_facts(locality, reference):
    if locality is None:
        return {"nombre": "", "pob": None, "urbana": None, "dist": None,
                "id": None, "municipio": "", "ambito": "", "codigo": ""}
    ambito = AMBITO.get(locality.complete_code)
    return {
        "id": locality.pk,
        "nombre": str(locality),
        "codigo": locality.complete_code,
        "pob": locality.population,
        "ambito": ambito or "",
        "urbana": None if not ambito else ambito == "U",
        "dist": distance_m(reference, locality),
        "municipio": str(locality.municipality or ""),
    }


def weighted_nearest(reference, municipality, exponent: float):
    """Localidad del municipio que minimiza distancia / población^e.

    La ponderación es la forma barata de castigar al caserío pegado al
    punto frente a la cabecera urbana un poco más lejos: con e = 0 es la
    regla actual (vecino más cercano a secas).
    """
    if reference is None or municipality is None:
        return None
    candidates = _locality_points(municipality.pk)
    if not candidates:
        return None
    origin = point_in_meters(*reference)
    best, best_score = None, None
    for locality, point in candidates:
        population = max(locality.population or 1, 1)
        score = origin.distance(point) / (population ** exponent)
        if best_score is None or score < best_score:
            best, best_score = locality, score
    return best


def si_no(value):
    return "" if value is None else ("sí" if value else "no")


def _weighted_id(reference, municipality, exponent: float):
    locality = weighted_nearest(reference, municipality, exponent)
    return locality.pk if locality else None


def main():
    rows, raw = [], []
    tally = {}
    seen = 0
    for location in located(with_project=True).iterator(chunk_size=500):
        seen += 1
        if location.type_location == "point":
            if location.latitude is None or location.longitude is None:
                continue
            resolution = resolve_point(
                location.latitude, location.longitude, location.state_id)
        else:
            resolution = resolve_geometry(location.geojson, location.state_id)
        reference = reference_point(location, resolution)
        differing, values = [], {}
        for name in COMPARED_FIELDS:
            captured = getattr(location, name)
            computed = computed_value(resolution, name)
            values[name] = (captured, computed)
            if captured is None:
                if computed is not None:
                    differing.append(name)
            elif computed is not None and computed.pk != captured.pk:
                differing.append(name)
        for name in COMPARED_FIELDS:
            captured, computed = values[name]
            if captured is not None:
                continue
            key = f"vacio_{FIELD_LABEL[name]}_{location.type_location}"
            tally[key] = tally.get(key, 0) + 1
            if computed is not None:
                llenable = f"{key}_llenable"
                tally[llenable] = tally.get(llenable, 0) + 1
        tally[f"revisadas_{location.type_location}"] = tally.get(
            f"revisadas_{location.type_location}", 0) + 1
        if not differing:
            continue
        captured_locality, computed_locality = values["locality"]
        captured_facts = locality_facts(captured_locality, reference)
        computed_facts = locality_facts(computed_locality, reference)
        crossed = [
            (municipality.name, round(measure, 1))
            for municipality, measure in getattr(
                resolution, "municipalities", [])]
        row = {
            "id": location.pk,
            "proyecto_id": location.project_id,
            "proyecto": str(location.project or ""),
            "tipo": location.type_location,
            "diferencias": "; ".join(
                FIELD_LABEL[name] for name in differing),
            "localidad_capturada_vacia": (
                "sí" if captured_locality is None else "no"),
            "pob_localidad_capturada": captured_facts["pob"],
            "pob_localidad_calculada": computed_facts["pob"],
            "urbana_capturada": si_no(captured_facts["urbana"]),
            "urbana_calculada": si_no(computed_facts["urbana"]),
            "dist_m_localidad_capturada": captured_facts["dist"],
            "dist_m_localidad_calculada": computed_facts["dist"],
            "municipios_atravesados": "; ".join(
                name for name, _ in crossed),
        }
        for name in COMPARED_FIELDS:
            captured, computed = values[name]
            captured_column, computed_column = COLUMN[name]
            row[captured_column] = str(captured or "")
            row[computed_column] = str(computed or "")
        rows.append(row)
        raw.append({
            **row,
            "diferencias_lista": differing,
            "referencia": reference,
            "estado_capturado_id": (
                values["state"][0].pk if values["state"][0] else None),
            "estado_calculado_id": (
                values["state"][1].pk if values["state"][1] else None),
            "municipio_capturado_id": (
                values["municipality"][0].pk
                if values["municipality"][0] else None),
            "municipio_calculado_id": (
                values["municipality"][1].pk
                if values["municipality"][1] else None),
            "localidad_capturada_datos": captured_facts,
            "localidad_calculada_datos": computed_facts,
            "municipios_atravesados_medida": crossed,
            "n_municipios_atravesados": len(crossed),
            "ponderada_raiz": _weighted_id(
                reference, values["municipality"][1], 0.5),
            "ponderada_cubica": _weighted_id(
                reference, values["municipality"][1], 1 / 3),
        })

    rows.sort(key=lambda item: (item["tipo"], item["diferencias"],
                                item["id"]))
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    OUT_TALLY.write_text(
        json.dumps(tally, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUT_JSONL.open("w", encoding="utf-8") as handle:
        for item in raw:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Revisadas: {seen}; con diferencia: {len(rows)}")
    print(f"CSV: {OUT_CSV}")
    print(f"JSONL: {OUT_JSONL}")


if __name__ == "__main__":
    main()
