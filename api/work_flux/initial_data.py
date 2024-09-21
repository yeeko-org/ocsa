from .models import StatusControl


class InitStatus:
    def __init__(self):
        init_status = [
            ("need_review", "validation", "Requiere revisión", "red", None),
            ("validated", "validation", "Aprobado", "green", None),
            ("need_reclassify", "validation", "Requiere re-clasificación", "red", None),
            ("could_reclassify", "validation", "Podría re-clasificarse", "yellow", None),
            ("rejected", "validation", "Rechazado", "red", None),
            # ("in_progress", "validation", "En proceso", "blue", "mdi-account-edit"),
            ("draft", "register", "Borrador", "blue", None),
            ("created", "register", "Creado", "green", None),
            ("discarded", "register", "Descartado", "red", None),
            ("approved_v1", "register", "Aprobado en v.1", "green", None),
            ("approved", "register", "Aprobado", "green", None),
            ("need_changes", "register", "Requiere cambios", "red", None),
            ("deleted", "register", "Eliminado", "red", None),
            ("need_new_checking", "register", "Requiere nueva revisión", "red", None),
        ]
        for name, group, public_name, color, icon in init_status:
            StatusControl.objects.get_or_create(
                name=name,
                defaults={
                    "group": group,
                    "public_name": public_name,
                    "color": color,
                    "icon": icon,   
                }
            )
