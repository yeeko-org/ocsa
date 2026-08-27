"""¿Cuánto deforma la simplificación a los polígonos municipales?

Lee `00mun.shp` tal como lo lee `load_geometries` (pyogrio.raw, WKB en
EPSG:6372) y compara el área de cada municipio antes y después de
`shapely.simplify(tolerancia)`. No toca la base ni escribe nada.

    python .claude/diagnostics/municipality_simplify_area.py [tolerancia]

La tolerancia por defecto es 50 m, la de `DEFAULT_SIMPLIFIED_M`.
"""

import sys
from pathlib import Path

from pyogrio.raw import read
from shapely import wkb as shapely_wkb

SHAPEFILE = Path(__file__).resolve().parents[2] / \
    "space_time/geo_files/00mun.shp"
TOP = 10
ALERT_RATIO = 0.01


def rows(tolerance: float) -> list[dict]:
    meta, _, geometries, fields = read(str(SHAPEFILE))
    columns = {name: index for index, name in enumerate(meta["fields"])}
    measured = []
    for position, raw in enumerate(geometries):
        if raw is None:
            continue
        geometry = shapely_wkb.loads(bytes(raw))
        before = geometry.area
        if before <= 0:
            continue
        after = geometry.simplify(tolerance).area
        measured.append({
            "code": (f"{fields[columns['CVE_ENT']][position]}-"
                     f"{fields[columns['CVE_MUN']][position]}"),
            "name": fields[columns["NOMGEO"]][position],
            "before": before,
            "after": after,
            "ratio": abs(after - before) / before,
        })
    return measured


def main() -> None:
    tolerance = float(sys.argv[1]) if len(sys.argv) > 1 else 50.0
    measured = rows(tolerance)
    measured.sort(key=lambda row: row["ratio"], reverse=True)
    smallest = min(measured, key=lambda row: row["before"])
    over = [row for row in measured if row["ratio"] > ALERT_RATIO]
    print(f"Municipios medidos: {len(measured)} (tolerancia {tolerance:g} m)")
    print(f"Con más de {ALERT_RATIO:.0%} de cambio de área: {len(over)}")
    print(f"Área mínima: {smallest['before'] / 1e6:.3f} km² "
          f"({smallest['code']} {smallest['name']}), "
          f"cambio {smallest['ratio']:.4%}")
    print(f"\nLos {TOP} de mayor cambio relativo:")
    header = f"{'clave':>8}  {'municipio':<32} {'km² antes':>10} " \
             f"{'km² después':>12} {'cambio':>9}"
    print(header)
    for row in measured[:TOP]:
        print(f"{row['code']:>8}  {row['name'][:32]:<32} "
              f"{row['before'] / 1e6:>10.3f} {row['after'] / 1e6:>12.3f} "
              f"{row['ratio']:>9.4%}")


if __name__ == "__main__":
    main()
