from .models import StatusControl


class InitStatus:
    def __init__(self):
        # name, group, public_name, color, icon, is_public, open_editor,
        # open_selectable, is_legacy, priority[, description]
        init_status = [
            ("proposed", "validation", "Propuesto",
                "blue", "lightbulb", False, True, True, False, 6),
            ("need_review", "validation", "Requiere revisión",
                "orange", "assignment_late", True, False, False, False, 2),
            ("rejected", "validation", "Rechazado",
                "red", "bug_report", False, False, False, False, 10),
            ("validated", "validation", "Aprobado",
                "green", "done_all", True, False, False, False, 14),
            ("need_reclassify", "validation", "Requiere re-clasificarse",
                "orange", "gpp_bad", True, False, False, False, 4),
            ("could_reclassify", "validation", "Podría re-clasificarse",
                "amber", "gpp_maybe", True, False, False, False, 8),
            ("original", "validation", "Original (v.1)",
                "light-green", "done", True, False, False, False, 12),
            ("yk_proposed", "validation", "Propuesto por Yeeko",
                "teal", "task", True, False, False, False, 12),
            ("expired", "validation", "Caducas (no usar)",
                "red", "disabled_by_default", True, False, False, False, 10,
                "Clasificaciones de la versión anterior que ya no serán usadas"),

            ("pre_captured", "register", "Pre-capturado",
                "indigo", "smart_toy", False, True, True, False, 0,
                "Fue Precapturado por la IA"),
            ("draft", "register", "Borrador",
                "blue", "edit_note", False, True, True, False, 8),
            ("created", "register", "Creado (para revisarse)",
                "green", "pending_actions", False, True, True, False, 6),
            ("need_changes", "register", "Requiere cambios",
                "orange", "new_releases", False, True, True, False, 2),
            ("need_new_checking", "register", "Requiere nueva revisión",
                "pink", "report_gmailerrorred", False, True, True, False, 4),
            ("approved", "register", "Aprobado",
                "green", "done_all", True, False, False, False, 16),
            ("discarded", "register", "Descartado",
                "red", "heart_broken", False, True, True, False, 10),
            ("deleted", "register", "Listo para segunda revisión",
                "red", "delete_forever", False, True, True, False, 12),
            ("approved_v1", "register", "Aprobado v.1",
                "light-green", "done", True, False, False, False, 14),

            ("empty", "location", "Vacío",
                "red", "location_off", False, True, False, False, 10),
            ("initial", "location", "Datos iniciales",
                "blue", "edit_note", False, True, True, False, 9),
            ("filled", "location", "Datos completos",
                "indigo", "edit_location", False, True, True, False, 2),
            ("need_consensus", "location", "Requiere consenso",
                "pink", "report_gmailerrorred", False, True, True, False, 3),
            ("finished", "location", "Finalizado",
                "green", "done_all", True, False, False, False, 14),
            ("Aproximado", "location", "Aprobado (Aproximado)",
                "cyan-darken-3", "rocket_launch", True, True, True, False, 1,
                ""),
            ("initial_v1", "location", "v1. Datos iniciales",
                "blue", "edit_note", False, True, False, False, 8),
            ("need_fix", "location", "v1. Requiere corrección",
                "orange", "not_listed_location", True, False, False, True, 4),
            ("could_enhance", "location", "v1. Podría mejorar",
                "orange", "auto_fix_high", True, False, False, False, 6),
            ("migrated_v1", "location", "v1. Migrado",
                "light-green", "done", True, False, False, False, 12),

            ("casual_case", "retro", "Caso típico",
                "indigo", "bug_report", True, True, True, False, 1,
                "Es un caso típico de mala clasificación"),
            ("other_retro", "retro", "Otra retro",
                "orange", "info", True, True, True, False, 0,
                "Cualquier otra retro deberá tener comentarios forzosamente "
                "para entender qué ocurre"),
            ("want_comment", "retro", "Aclaración deseable",
                "lime", "help_outline", True, True, True, False, 8,
                "Una de las partes no entendió del todo la razón o se "
                "considera que podría ser distinta la"),
            ("required_comment", "retro", "Aclaración requerida",
                "yellow", "warning", True, True, True, False, 5,
                "Una de las partes considera que no la clasificación debe "
                "revisarse"),
            ("without_comments", "retro", "Revisado",
                "green", "done", True, True, True, False, 15,
                "Solo para marcar que ya está revisado"),
            ("no_comments", "retro", "Sin comentarios",
                "grey", "airline_stops", True, True, True, False, 0,
                "No hay comentarios que agregar, tamopco es perfectamente "
                "claro, pero no requiere aclaración."),
        ]
        order = -1
        for data in init_status:
            name = data[0]
            group = data[1]
            public_name = data[2]
            color = data[3]
            icon = data[4]
            is_public = data[5]
            open_editor = data[6]
            open_selectable = data[7]
            is_legacy = data[8]
            try:
                priority = data[9]
            except IndexError:
                priority = 99
            try:
                description = data[10]
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
            if group == "retro" and order < 60:
                order = 60
            status.order = order
            status.open_editor = open_editor
            status.open_selectable = open_selectable
            status.is_legacy = is_legacy
            status.priority = priority
            status.description = description
            status.save()
