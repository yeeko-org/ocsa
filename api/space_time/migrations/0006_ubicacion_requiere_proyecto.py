import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0001_initial"),
        ("space_time", "0005_quitar_ubicaciones_de_eventos_e_impactos"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="project",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="locations",
                to="project.project",
            ),
        ),
    ]
