"""Da el status «Original (v.1)» a los actores sin status de validación.

Sin status, los permisos del actor truenan al leer `open_editor` y la
fusión del dashboard no puede borrarlo. La reversa no hace nada: tras
aplicarla ya no se distingue qué actores no tenían status.
"""

from django.db import migrations


def set_original_status(apps, schema_editor):
    Actor = apps.get_model("actor", "Actor")
    Actor.objects.filter(status_validation__isnull=True).update(
        status_validation_id="original")


class Migration(migrations.Migration):

    dependencies = [
        ("actor", "0006_remove_interest_interest_type"),
        ("work_flux", "0008_statusgroup"),
    ]

    operations = [
        migrations.RunPython(set_original_status, migrations.RunPython.noop),
    ]
