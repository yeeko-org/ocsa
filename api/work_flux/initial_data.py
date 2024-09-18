from .models import StatusControl


class InitStatus:
    def __init__(self):
        init_status = [
            ("need_review", "validation", "Requiere revisión", "red", None),
            ("approved", "validation", "Aprobado", "green", None),
            ("rejected", "validation", "Rechazado", "red", None),
            ("need_reclassify", "validation", "Requiere re-clasificación", "red", None),
            ("could_reclassify", "validation", "Podría re-clasificarse", "yellow", None),
            # ("in_progress", "validation", "En proceso", "blue", "mdi-account-edit"),
        ]
        for name, group, public_name, color, icon in init_status:
            StatusControl.objects.get_or_create(
                name=name,
                group=group,
                public_name=public_name,
                color=color,
            )
