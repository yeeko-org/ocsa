from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_remove_project_incongruent_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='alternative_name',
            new_name='alternative_names',
        ),
        migrations.AlterField(
            model_name='project',
            name='alternative_names',
            field=models.TextField(blank=True, null=True, verbose_name='Nombres alternativos'),
        ),
    ]
