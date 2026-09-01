import django.db.models.deletion
from django.db import migrations, models


# key_name, public_name, order, hide_when_empty — el orden viene del
# registro que el front llevaba a mano en `nuxt/composables/filters.js`;
# los dos «6» son los que ya tenía, no un empate nuevo.
INITIAL_GROUPS = [
    ("register", "Registro", 4, False),
    ("validation", "Validación", 5, False),
    ("location", "Ubicación", 6, False),
    ("retro", "Feedback", 6, True),
]


def seed_groups(apps, schema_editor):
    StatusGroup = apps.get_model("work_flux", "StatusGroup")
    StatusControl = apps.get_model("work_flux", "StatusControl")
    for key_name, public_name, order, hide_when_empty in INITIAL_GROUPS:
        StatusGroup.objects.get_or_create(
            key_name=key_name,
            defaults={
                "public_name": public_name, "order": order,
                "hide_when_empty": hide_when_empty},
        )
    known = set(StatusGroup.objects.values_list("key_name", flat=True))
    orphans = sorted(
        StatusControl.objects
        .exclude(group__in=known)
        .values_list("name", "group"))
    if orphans:
        detail = ", ".join(
            f"{name} (group={group!r})" for name, group in orphans)
        raise RuntimeError(
            "Hay StatusControl con un grupo que no existe en StatusGroup; "
            "reasignarlos a mano antes de migrar en vez de adivinar aquí: "
            f"{detail}")


def drop_groups(apps, schema_editor):
    StatusGroup = apps.get_model("work_flux", "StatusGroup")
    keys = [key_name for key_name, *_ in INITIAL_GROUPS]
    StatusGroup.objects.filter(key_name__in=keys).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("work_flux", "0007_rename_is_deleted_to_is_legacy"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusGroup",
            fields=[
                ("key_name", models.CharField(
                    max_length=30, primary_key=True, serialize=False)),
                ("public_name", models.CharField(max_length=120)),
                ("order", models.IntegerField(default=0)),
                ("hidden", models.BooleanField(
                    default=False,
                    verbose_name="oculto en la barra de filtros")),
                ("hide_when_empty", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Grupo de status",
                "verbose_name_plural": "Grupos de status",
                "ordering": ["order"],
            },
        ),
        migrations.RunPython(seed_groups, drop_groups),
        migrations.AlterField(
            model_name="statuscontrol",
            name="group",
            field=models.ForeignKey(
                default="validation",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="statuses",
                to="work_flux.statusgroup",
                verbose_name="grupo de status"),
        ),
    ]
