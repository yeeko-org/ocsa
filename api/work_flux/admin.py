from django.contrib import admin
from work_flux.models import StatusControl


@admin.register(StatusControl)
class StatusControlAdmin(admin.ModelAdmin):
    list_display = [
        "public_name", "name", "group", "order", "is_public",
        "open_editor", "open_selectable", "color", "icon", "priority"]
    list_editable = ["order", "color", "icon", "priority"]
    list_filter = ["group"]
