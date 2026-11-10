"""Vacía el propósito de los eventos cuyo grupo no lo usa (task-125).

Son restos de mecanismos legales que cambiaron de tipo. El criterio es
la misma bandera con la que el dashboard decide si muestra el selector
(`EventGroup.show_position`), no una lista de grupos.
"""

from django.db import migrations


def clear_stray_purpose(apps, schema_editor):
    Event = apps.get_model("event", "Event")
    Event.objects.filter(
        purpose__isnull=False,
        event_type__event_group__show_position=False,
    ).update(purpose=None)


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0017_event_reclassification_confidence_and_more"),
    ]

    operations = [
        migrations.RunPython(clear_stray_purpose, migrations.RunPython.noop),
    ]
