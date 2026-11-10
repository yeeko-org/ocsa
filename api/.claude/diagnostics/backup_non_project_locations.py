"""Respaldo previo a quitar las ubicaciones de eventos e impactos.

Solo lectura (la transacción se abre READ ONLY). Se corre contra
producción justo antes de `migrate`: la 0004 de `space_time` borra toda
`Location` sin proyecto, y la 0005 quita `event_id`/`impact_id`
(adr-0035, task-122). Por eso lee con SQL crudo y no con el modelo: el
modelo del working tree ya no tiene esas dos columnas.

Escribe en el directorio de salida:

- `ubicaciones_sin_proyecto_<fecha>.json`: cada fila de
  `space_time_location` sin proyecto con todas sus columnas, sus filas
  del M2M `municipalities` y las de `task_clickhistory` que el borrado
  arrastra en cascada; más el propósito de los eventos que la 0018 de
  `event` deja en nulo. Cada tabla va con sus columnas tal cual, para
  restaurar con `json_populate_recordset` tras volver a crear las
  columnas.
- `proyectos_sin_ubicacion_<fecha>.xlsx`: para el equipo, los proyectos
  sin ubicación propia con las entidades y los municipios que aparecen
  en las ubicaciones de sus eventos y afectaciones.

Uso:
    python api/.claude/diagnostics/backup_non_project_locations.py <dir>
    DATABASE_NAME=ocsa-prod-20261108 \\
        python api/.claude/diagnostics/backup_non_project_locations.py <dir>
"""
import datetime
import json
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import connection, transaction  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Font  # noqa: E402

DOOMED = "SELECT id FROM space_time_location WHERE project_id IS NULL"

TABLES = {
    "space_time_location": f"""
        SELECT row_to_json(t) FROM space_time_location t
        WHERE t.id IN ({DOOMED}) ORDER BY t.id""",
    "space_time_location_municipalities": f"""
        SELECT row_to_json(t) FROM space_time_location_municipalities t
        WHERE t.location_id IN ({DOOMED}) ORDER BY t.id""",
    "task_clickhistory": f"""
        SELECT row_to_json(t) FROM task_clickhistory t
        WHERE t.location_id IN ({DOOMED}) ORDER BY t.id""",
    # Lo que la 0018 de `event` vacía: misma condición que la migración.
    "event_event.purpose_id": """
        SELECT json_build_object('id', e.id, 'purpose_id', e.purpose_id)
        FROM event_event e
        JOIN event_eventtype et ON et.id = e.event_type_id
        JOIN event_eventgroup eg ON eg.id = et.event_group_id
        WHERE e.purpose_id IS NOT NULL AND NOT eg.show_position
        ORDER BY e.id""",
}

# Ubicaciones de evento o de afectación cuyo proyecto (por la mención)
# no tiene ninguna ubicación propia.
TEAM_SHEET = """
    WITH borrowed AS (
        SELECT m.project_id, 'event' AS origin, l.id AS location_id,
               l.state_id, l.municipality_id
        FROM space_time_location l
        JOIN event_event e ON e.id = l.event_id
        JOIN source_mention m ON m.id = e.mention_id
        WHERE l.project_id IS NULL
        UNION ALL
        SELECT m.project_id, 'impact', l.id, l.state_id, l.municipality_id
        FROM space_time_location l
        JOIN impact_impact i ON i.id = l.impact_id
        JOIN source_mention m ON m.id = i.mention_id
        WHERE l.project_id IS NULL
    )
    SELECT p.id, p.name,
           COUNT(DISTINCT b.location_id) FILTER (WHERE b.origin = 'event'),
           COUNT(DISTINCT b.location_id) FILTER (WHERE b.origin = 'impact'),
           STRING_AGG(DISTINCT s.name, '; '),
           STRING_AGG(DISTINCT mu.name || ' (' || ms.name || ')', '; ')
    FROM borrowed b
    JOIN project_project p ON p.id = b.project_id
    LEFT JOIN space_time_state s ON s.id = b.state_id
    LEFT JOIN space_time_municipality mu ON mu.id = b.municipality_id
    LEFT JOIN space_time_state ms ON ms.id = mu.state_id
    WHERE NOT EXISTS (
        SELECT 1 FROM space_time_location own WHERE own.project_id = p.id)
    GROUP BY p.id, p.name
    ORDER BY p.name
"""

HEADERS = [
    ("ID del proyecto", 10), ("Proyecto", 45),
    ("Ubicaciones de eventos", 12), ("Ubicaciones de afectaciones", 12),
    ("Entidades", 35), ("Municipios (entidad)", 70),
]


def fetch_json(cursor, sql: str) -> list:
    cursor.execute(sql)
    # Según el adaptador, json llega ya decodificado o como texto.
    return [value if isinstance(value, dict) else json.loads(value)
            for (value,) in cursor.fetchall()]


def write_sheet(rows: list, path: str) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Proyectos sin ubicación"
    for column, (title, width) in enumerate(HEADERS, start=1):
        cell = sheet.cell(row=1, column=column, value=title)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        letter = cell.column_letter
        sheet.column_dimensions[letter].width = width
    for row in rows:
        sheet.append(list(row))
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    sheet.freeze_panes = "A2"
    workbook.save(path)


def main(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SET TRANSACTION READ ONLY")
        cursor.execute("SELECT current_database(), now()")
        database, now = cursor.fetchone()
        tables = {name: fetch_json(cursor, sql)
                  for name, sql in TABLES.items()}
        cursor.execute(TEAM_SHEET)
        team_rows = cursor.fetchall()

    locations = tables["space_time_location"]
    payload = {
        "database": database,
        "dumped_at": now.isoformat(),
        "counts": {name: len(rows) for name, rows in tables.items()},
        "by_owner": {
            "event": sum(1 for r in locations if r["event_id"]),
            "impact": sum(1 for r in locations if r["impact_id"]),
            "orphan": sum(1 for r in locations
                          if not r["event_id"] and not r["impact_id"]),
        },
        "tables": tables,
    }
    json_path = os.path.join(out_dir, f"ubicaciones_sin_proyecto_{stamp}.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, default=str)
    xlsx_path = os.path.join(out_dir, f"proyectos_sin_ubicacion_{stamp}.xlsx")
    write_sheet(team_rows, xlsx_path)

    print(f"Base: {database}")
    for name, count in payload["counts"].items():
        print(f"  {name}: {count}")
    print(f"  ubicaciones por dueño: {payload['by_owner']}")
    print(f"  proyectos sin ubicación propia: {len(team_rows)}")
    print(json_path)
    print(xlsx_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
