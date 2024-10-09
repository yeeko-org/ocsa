from .models import StatusControl


class InitStatus:
    def __init__(self):
        init_status = [
            ("validated", "validation", "Aprobado",
                "green", "verified", True),
            ("proposed", "validation", "Propuesto",
                "blue", "lightbulb", False),
            ("need_review", "validation", "Requiere revisión",
                "pink", "dangerous", True),
            ("need_reclassify", "validation", "Requiere re-clasificación",
                "pink", "gpp_bad", True),
            ("could_reclassify", "validation", "Podría re-clasificarse",
                "orange", "gpp_maybe", True),
            ("rejected", "validation", "Rechazado",
                "red", "bug_report", False),
            ("original", "validation", "Original (v.1)",
                "light-green", "done", True),

            ("draft", "register", "Borrador",
                "blue", "edit_note", False),
            ("created", "register", "Creado",
                "green", "pending_actions", False),
            ("approved", "register", "Aprobado",
                "green", "done_all", True),
            ("need_changes", "register", "Requiere cambios",
                "orange", "new_releases", False),
            ("need_new_checking", "register", "Requiere nueva revisión",
                "pink", "report_gmailerrorred", False),
            ("discarded", "register", "Descartado",
                "red", "heart_broken", False),
            ("deleted", "register", "Eliminado",
                "red", "delete_forever", False),
            ("approved_v1", "register", "Aprobado v.1",
                "light-green", "done", True),
        ]
        order = -1
        for name, group, public_name, color, icon, is_public in init_status:
            status, _ = StatusControl.objects.get_or_create(
                name=name
            )
            status.group = group
            status.public_name = public_name
            status.color = color
            status.icon = icon
            status.is_public = is_public
            order += 2
            if group == "register" and order < 20:
                order = 20
            status.order = order
            status.save()
