from .models import StatusControl


class InitStatus:
    def __init__(self):
        init_status = [
            ("need_review", "validation", "Requiere revisión", "red", "mdi-alert-circle"),
            ("approved", "validation", "Aprobado", "green", "mdi-check-circle"),
            ("rejected", "validation", "Rechazado", "red", "mdi-close-circle"),
            ("need_reclassify", "validation", "Requiere re-clasificación", "red", "mdi-alert-circle"),
            ("could_reclassify", "validation", "Podría re-clasificarse", "yellow", "mdi-alert-circle"),
            # ("in_progress", "validation", "En proceso", "blue", "mdi-account-edit"),
        ]
        for name, group, public_name, color, icon in init_status:
            StatusControl.objects.get_or_create(
                name=name,
                group=group,
                public_name=public_name,
                color=color,
                icon=icon
            )
