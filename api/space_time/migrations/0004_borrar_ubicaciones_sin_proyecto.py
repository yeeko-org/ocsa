"""Borra toda ubicación sin proyecto: las de eventos, las de impactos y
las huérfanas (adr-0033, task-122).

Va sola, separada de quitar las columnas: los dos FK que apuntan a la
tabla (`municipalities` y `task_clickhistory`) son DEFERRABLE INITIALLY
DEFERRED, y PostgreSQL no deja alterar la tabla en la misma transacción
que borró filas referenciadas («pending trigger events»).

El respaldo previo lo escribe
`.claude/diagnostics/backup_non_project_locations.py`; por eso la
reversa no restaura nada.
"""

from django.db import migrations


def delete_non_project_locations(apps, schema_editor):
    Location = apps.get_model("space_time", "Location")
    # El modelo histórico no corre Location.delete(); no hace falta: sin
    # proyecto no hay status_location de proyecto que rederivar.
    Location.objects.filter(project__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("space_time", "0003_quitar_localidades_cercanas"),
    ]

    operations = [
        migrations.RunPython(
            delete_non_project_locations, migrations.RunPython.noop),
    ]
