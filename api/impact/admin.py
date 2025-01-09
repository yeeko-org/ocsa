# DJANGO ADMIN
from django.contrib import admin
from impact.models import ImpactType


class ImpactTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_social', 'short_name')
    search_fields = ('name', 'description')
    list_filter = ('impact_group')
    list_editable = ('order',)
    model = ImpactType
