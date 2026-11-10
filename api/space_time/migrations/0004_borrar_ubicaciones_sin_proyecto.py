"""Borra toda ubicación sin proyecto: las de eventos, las de impactos y
las huérfanas (adr-0033, task-122).

Va sola, separada de quitar las columnas: los dos FK que apuntan a la
tabla (`municipalities` y `task_clickhistory`) son DEFERRABLE INITIALLY
DEFERRED, y PostgreSQL no deja alterar la tabla en la misma transacción
que borró filas referenciadas («pending trigger events»).

El respaldo previo lo escribe
`api/.claude/diagnostics/backup_non_project_locations.py`; por eso la
reversa no restaura nada.

Los clics de esas ubicaciones sobreviven (task-140): el modelo histórico
no dispara la señal `pre_delete` que escribe `deleted_origin`, así que
el rastro se escribe aquí, antes de borrar.
"""

from django.db import migrations
from django.utils import timezone


# Copies of task.deleted_origin as of this migration: a historical
# migration must not change when that module does.
def location_label(latitude, longitude, details):
    if latitude and longitude:
        return f"{latitude}, {longitude}"
    return details or "Ubicación sin coordenadas ni detalles"


def build_origin(model_name, pk, label):
    return {
        "model": model_name,
        "id": pk,
        "label": label,
        "date": timezone.now().isoformat(timespec="seconds"),
    }


def delete_non_project_locations(apps, schema_editor):
    Location = apps.get_model("space_time", "Location")
    ClickHistory = apps.get_model("task", "ClickHistory")
    doomed = Location.objects.filter(project__isnull=True)
    clicked = doomed.filter(clicks__isnull=False).distinct().values(
        "id", "latitude", "longitude", "details")
    for row in clicked:
        label = location_label(
            row["latitude"], row["longitude"], row["details"])
        ClickHistory.objects.filter(location_id=row["id"]).update(
            deleted_origin=build_origin("location", row["id"], label))
    # El modelo histórico no corre Location.delete(); no hace falta: sin
    # proyecto no hay status_location de proyecto que rederivar.
    doomed.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("space_time", "0003_quitar_localidades_cercanas"),
        ("task", "0005_historial_sobrevive_al_borrado"),
    ]

    operations = [
        migrations.RunPython(
            delete_non_project_locations, migrations.RunPython.noop),
    ]
