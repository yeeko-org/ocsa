from django.contrib import admin
from work_flux.models import StatusControl


@admin.register(StatusControl)
class StatusControlAdmin(admin.ModelAdmin):
    list_display = [
        "public_name", "name", "group", "order", "is_public", "color", "icon"]
    list_editable = ["order", "color", "icon"]
    list_filter = ["group"]
