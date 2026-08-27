"""Solo lectura: inventario de `Location.comments` frente al backfill.

Replica la selección de `geolocate_locations --fill` sin escribir nada:
corre `apply_geolocation` con `write_relations=False` y descarta el
objeto, así que ninguna columna ni M2M se toca.
"""
import json
import os
import sys
from collections import Counter

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from space_time.geolocate import apply_geolocation  # noqa: E402
from space_time.geometry import has_geometry, has_geometry_q  # noqa: E402
from space_time.models import Location  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "location_comments_raw.jsonl")

with_comments = Location.objects.exclude(comments__isnull=True).exclude(
    comments__exact="").select_related(
    "state", "municipality", "locality", "project", "status_location")

total_all = Location.objects.count()
print(f"Ubicaciones totales: {total_all}")
print(f"Con comments no vacío: {with_comments.count()}")

by_type = Counter()
by_geom = Counter()
by_status = Counter()
by_touch = Counter()
rows = []
for loc in with_comments.iterator(chunk_size=500):
    geom = has_geometry(loc)
    empties = [n for n in ("state", "municipality", "locality")
               if getattr(loc, f"{n}_id") is None]
    selected = geom and (bool(empties) or loc.type_location != "point")
    by_type[loc.type_location] += 1
    by_geom[geom] += 1
    by_status[str(loc.status_location or "sin estatus")] += 1
    by_touch[selected] += 1
    filled = []
    if geom:
        filled = apply_geolocation(
            loc, geometry_changed=True, write_relations=False)
    rows.append({
        "id": loc.pk,
        "proyecto": str(loc.project or ""),
        "proyecto_id": loc.project_id,
        "evento_id": loc.event_id,
        "impacto_id": loc.impact_id,
        "tipo": loc.type_location,
        "status": str(loc.status_location or ""),
        "geom": geom,
        "vacios": empties,
        "seleccionada": selected,
        "campos_que_llenaria": filled,
        "details": (loc.details or "")[:300],
        "comment": loc.comments,
    })

print("\nPor tipo:", dict(by_type))
print("Con geometría:", {str(k): v for k, v in by_geom.items()})
print("Tocadas por --fill (estructural):",
      {str(k): v for k, v in by_touch.items()})
print("\nPor status_location:")
for name, count in by_status.most_common():
    print(f"  {name}: {count}")

# Cruces
cross = Counter()
for r in rows:
    cross[(r["tipo"], r["seleccionada"])] += 1
print("\nTipo x seleccionada:", {f"{k[0]}/{k[1]}": v for k, v in cross.items()})
cross2 = Counter()
for r in rows:
    if r["seleccionada"]:
        cross2[r["status"] or "sin estatus"] += 1
print("Status de las seleccionadas:", dict(cross2))
real = [r for r in rows if r["campos_que_llenaria"]]
print(f"\nCon comentario y con cambio REAL del fill: {len(real)}")
fields = Counter()
for r in real:
    for f in r["campos_que_llenaria"]:
        fields[f] += 1
print("Campos que llenaría:", dict(fields))

with open(OUT, "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"\nJSONL: {os.path.normpath(OUT)}")
