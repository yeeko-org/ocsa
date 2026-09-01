from django.contrib import admin
from work_flux.models import StatusControl, StatusGroup


@admin.register(StatusGroup)
class StatusGroupAdmin(admin.ModelAdmin):
    list_display = [
        "public_name", "key_name", "order", "hidden", "hide_when_empty"]
    list_editable = ["order", "hidden", "hide_when_empty"]


@admin.register(StatusControl)
class StatusControlAdmin(admin.ModelAdmin):
    list_display = [
        "public_name", "name", "group", "order", "is_public",
        "open_editor", "open_selectable", "is_legacy", "color", "icon",
        "priority"]
    list_editable = ["order", "color", "icon", "priority"]
    list_filter = ["group"]
    list_select_related = ["group"]
