

from django.db import migrations
from django.contrib.postgres.operations import CreateExtension


class Migration(migrations.Migration):

    dependencies = [
        ('actor', '0002_initial'),
    ]

    operations = [
        CreateExtension('unaccent'),
    ]