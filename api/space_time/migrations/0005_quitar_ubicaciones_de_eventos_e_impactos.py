from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("space_time", "0004_borrar_ubicaciones_sin_proyecto"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="location",
            name="event",
        ),
        migrations.RemoveField(
            model_name="location",
            name="impact",
        ),
    ]
