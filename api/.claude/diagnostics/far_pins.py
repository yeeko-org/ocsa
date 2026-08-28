"""Pines lejos de lo capturado: puntos fuera de su municipio o su estado.

Solo lectura: saca a CSV lo que `space_time/far_pins.py` selecciona, que
es la misma selección que aplica el comando
`flag_locations_for_review`.

    venv/bin/python .claude/diagnostics/far_pins.py [umbral_km]
"""

import csv
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402

django.setup()

from space_time.far_pins import THRESHOLD_KM, name_of, scan  # noqa: E402

OUT_CSV = Path(f".claude/far_pins_{date.today().isoformat()}.csv")
HEADERS = [
    "location_id", "project_id", "project_name", "status_location",
    "state_captured", "state_computed",
    "municipality_captured", "municipality_computed",
    "km_to_captured_municipality", "km_to_captured_state",
]


def main() -> None:
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else THRESHOLD_KM
    found, seen = scan(threshold)
    rows = []
    for pin in found:
        location, resolution = pin.location, pin.resolution
        rows.append({
            "location_id": location.pk,
            "project_id": location.project_id,
            "project_name": str(location.project or ""),
            "status_location": (
                location.status_location.public_name
                if location.status_location_id else ""),
            "state_captured": name_of(location.state),
            "state_computed": name_of(resolution.state),
            "municipality_captured": name_of(location.municipality),
            "municipality_computed": name_of(resolution.municipality),
            "km_to_captured_municipality": pin.to_municipality,
            "km_to_captured_state": pin.to_state,
        })
    rows.sort(
        key=lambda row: max(row["km_to_captured_municipality"] or 0.0,
                            row["km_to_captured_state"] or 0.0),
        reverse=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Puntos con proyecto y coordenadas: {seen}")
    print(f"Umbral: {threshold} km; filas: {len(rows)}")
    print(f"CSV: {OUT_CSV}")


if __name__ == "__main__":
    main()
