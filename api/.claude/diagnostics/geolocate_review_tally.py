"""Conteos del CSV de `geolocate_locations --review` (docs `task-83`).

Insumo para decidir la corrida real de `--fill`: cuántas filas toca,
qué toca en cada una, y cómo se reparte eso por estatus de ubicación.
No lee la base ni escribe nada fuera del `.md` de salida.

    venv/bin/python .claude/diagnostics/geolocate_review_tally.py \
        .claude/geolocate_review_2026-08-27c.csv
"""

import sys
from collections import Counter
from pathlib import Path

import pandas

CHANGES = ("estado", "municipio", "localidad", "municipios_atravesados",
           "centroide")
APPROXIMATE_PUBLIC_NAME = "Aprobado (Aproximado)"


def load(path: Path) -> pandas.DataFrame:
    frame = pandas.read_csv(path, encoding="utf-8-sig", dtype=str)
    return frame.fillna("")


def split(value: str) -> list:
    return [part for part in value.split("; ") if part]


def table(rows: list, headers: tuple) -> list:
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |"
              for row in rows]
    return lines


def suppressed(frame: pandas.DataFrame) -> pandas.DataFrame:
    """Filas donde la salvaguarda impidió escribir la localidad.

    Se reconocen por lo que el CSV ya trae: punto aproximado, con
    localidad vacía y una calculada disponible, y aun así `localidad`
    no aparece entre los cambios.
    """
    return frame[
        (frame["tipo"] == "point")
        & (frame["status_location"] == APPROXIMATE_PUBLIC_NAME)
        & (frame["locality_capturado"] == "")
        & (frame["locality_calculado"] != "")
        & ~frame["cambios_fill"].apply(
            lambda value: "localidad" in split(value))
    ]


def build(frame: pandas.DataFrame, source: Path) -> str:
    changes = frame["cambios_fill"].apply(split)
    with_changes = frame[changes.apply(bool)]
    lines = [
        f"# Conteo de `{source.name}`",
        "",
        f"Universo (ubicaciones con proyecto y geometría): **{len(frame)}**",
        f"Filas que `--fill` cambiaría: **{len(with_changes)}**",
        f"Filas sin cambio alguno: **{len(frame) - len(with_changes)}**",
        f"Filas con alguna diferencia entre capturado y calculado: "
        f"**{(frame['diferencias'] != '').sum()}**",
        "",
        "## Por tipo de cambio",
        "",
    ]
    per_change = Counter(item for row in changes for item in row)
    lines += table(
        [(name, per_change.get(name, 0)) for name in CHANGES],
        ("cambio", "filas"))

    lines += ["", "## Por combinación de cambios", ""]
    combos = Counter(
        "; ".join(row) if row else "(sin cambios)" for row in changes)
    lines += table(
        sorted(combos.items(), key=lambda pair: -pair[1]),
        ("combinación", "filas"))

    lines += ["", "## Tipo de cambio × tipo de geometría", ""]
    by_type = Counter(
        (row.tipo or "(sin tipo)", item)
        for row, items in zip(frame.itertuples(), changes)
        for item in items)
    types = sorted({kind for kind, _ in by_type})
    lines += table(
        [tuple([kind]
               + [by_type.get((kind, name), 0) for name in CHANGES]
               + [sum(1 for row in frame.itertuples()
                      if (row.tipo or "(sin tipo)") == kind)])
         for kind in types],
        tuple(["tipo"] + list(CHANGES) + ["filas del tipo"]))

    lines += ["", "## Tipo de cambio × estatus de la ubicación", ""]
    pairs = Counter(
        (row.status_location or "(sin estatus)", item)
        for row, items in zip(frame.itertuples(), changes)
        for item in items)
    statuses = sorted({status for status, _ in pairs})
    lines += table(
        [tuple([status]
               + [pairs.get((status, name), 0) for name in CHANGES]
               + [sum(1 for row in frame.itertuples()
                      if (row.status_location or "(sin estatus)") == status)])
         for status in statuses],
        tuple(["estatus"] + list(CHANGES) + ["filas del estatus"]))

    state_rows = frame[frame["diferencias"].apply(
        lambda value: "estado" in split(value))]
    lines += [
        "", "## Discrepancias de entidad", "",
        "Filas donde el estado capturado y el calculado no coinciden, o "
        "donde el capturado está vacío y el motor sí resolvió uno. Solo "
        "aparecen en puntos: en un trazo el estado no se calcula por "
        "polígonos, se hereda del municipio base.",
        "",
        f"Filas con `estado` en `diferencias`: **{len(state_rows)}**",
        "",
    ]
    if len(state_rows):
        lines += table(
            [(row.id, row.tipo, row.state_capturado or "(vacío)",
              row.state_calculado or "(vacío)",
              row.status_location or "(sin estatus)",
              "sí" if "estado" in split(row.cambios_fill) else "no")
             for row in state_rows.itertuples()],
            ("id", "tipo", "entidad capturada", "entidad calculada",
             "status_location", "`--fill` la escribiría"))

    blocked = suppressed(frame)
    lines += [
        "", "## Salvaguarda de los puntos «Aprobado (Aproximado)»", "",
        f"Filas donde la salvaguarda impidió escribir `locality`: "
        f"**{len(blocked)}**",
        "",
    ]
    if len(blocked):
        lines += table(
            [(row.id, row.proyecto, row.locality_calculado)
             for row in blocked.itertuples()],
            ("id", "proyecto", "localidad que se habría escrito"))
    return "\n".join(lines) + "\n"


def main() -> None:
    source = Path(sys.argv[1])
    out = source.with_name(source.stem + "_tally.md")
    out.write_text(build(load(source), source), encoding="utf-8")
    print(f"Conteo: {out}")


if __name__ == "__main__":
    main()
