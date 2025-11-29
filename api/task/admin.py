from django.contrib import admin
from .models import ClickHistory


class ClickHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "date_start", "action", "get_related_object"]
    raw_id_fields = ["user", "note", "article", "project", "location"]
    list_filter = ["action", "user", "date_start"]

    def get_related_object(self, obj):
        """Retorna el objeto relacionado con su tipo como prefijo."""
        if obj.note:
            return f"Nota: {obj.note}"
        elif obj.article:
            return f"Artículo: {obj.article}"
        elif obj.project:
            return f"Proyecto: {obj.project}"
        elif obj.location:
            return f"Ubicación: {obj.location}"
        return "-"

    get_related_object.short_description = "Objeto"


admin.site.register(ClickHistory, ClickHistoryAdmin)
