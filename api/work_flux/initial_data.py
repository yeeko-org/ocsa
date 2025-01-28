from .models import StatusControl


class InitStatus:
    def __init__(self):
        init_status = [
            ("proposed", "validation", "Propuesto",
                "blue", "lightbulb", False, True, False, 6),
            ("need_review", "validation", "Requiere revisión",
                "orange", "assignment_late", True, True, False, 2),
            ("rejected", "validation", "Rechazado",
                "red", "bug_report", False, False, False, 10),
            ("validated", "validation", "Aprobado",
                "green", "done_all", True, False, False, 14),
            ("need_reclassify", "validation", "Requiere re-clasificarse",
                "orange", "gpp_bad", True, False, False, 4),
            ("could_reclassify", "validation", "Podría re-clasificarse",
                "amber", "gpp_maybe", True, True, False, 8),
            ("original", "validation", "Original (v.1)",
                "light-green", "done", True, False, False, 12),
            ("yk_proposed", "validation", "Propuesto por Yeeko",
                "teal", "task", True, False, False, 12),
            ("expired", "validation", "Caducas (no usar)",
                "red", "disabled_by_default", True, False, False, 10,
                "Clasificaciones de la versión anterior que ya no serán usadas"),
            # is_public, open_editor, is_deleted
            ("draft", "register", "Borrador",
                "blue", "edit_note", False, True, False, 8),
            ("created", "register", "Creado (para revisarse)",
                "green", "pending_actions", False, True, False, 6),
            ("need_changes", "register", "Requiere cambios",
                "orange", "new_releases", False, False, False, 2),
            ("need_new_checking", "register", "Requiere nueva revisión",
                "pink", "report_gmailerrorred", False, True, False, 4),
            ("approved", "register", "Aprobado",
                "green", "done_all", True, False, False, 16),
            ("discarded", "register", "Descartado",
                "red", "heart_broken", False, True, False, 10),
            ("deleted", "register", "Eliminado",
                "red", "delete_forever", False, False, True, 12),
            ("could_fix", "register", "Podría corregirse v.1",
                "orange", "new_releases", True, False, False, 14),
            ("approved_v1", "register", "Aprobado v.1",
                "light-green", "done", True, False, False, 14),

            ("empty", "location", "Vacío",
                "red", "location_off", False, True, False, 10),
            ("initial", "location", "Datos iniciales",
                "blue", "edit_note", False, True, False, 9),
            ("filled", "location", "Datos completos",
                "indigo", "edit_location", False, True, False, 2),
            ("need_consensus", "location", "Requiere consenso",
                "pink", "report_gmailerrorred", False, True, False, 3),
            ("finished", "location", "Finalizado",
                "green", "done_all", True, False, False, 14),
            ("initial_v1", "location", "v1. Datos iniciales",
                "blue", "edit_note", False, False, False, 8),
            ("need_fix", "location", "v1. Requiere corrección",
                "orange", "not_listed_location", True, False, False, 4),
            ("could_enhance", "location", "v1. Podría mejorar",
                "orange", "auto_fix_high", True, False, False, 6),
            ("migrated_v1", "location", "v1. Migrado",
                "light-green", "done", True, False, False, 12),
        ]
        order = -1
        for data in init_status:
            # name, group, public_name, color, icon, is_public,
            # open_editor, is_deleted = data
            name = data[0]
            group = data[1]
            public_name = data[2]
            color = data[3]
            icon = data[4]
            is_public = data[5]
            open_editor = data[6]
            is_deleted = data[7]
            try:
                priority = data[8]
            except IndexError:
                priority = 99
            try:
                description = data[9]
            except IndexError:
                description = None
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
            if group == "location" and order < 40:
                order = 40
            status.order = order
            status.open_editor = open_editor
            status.is_deleted = is_deleted
            status.priority = priority
            status.description = description
            status.save()
