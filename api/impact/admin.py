# DJANGO ADMIN
from django.contrib import admin
from impact.models import ImpactType


class ImpactTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'has_subtype', 'is_social', 'short_name')
    search_fields = ('name', 'description')
    list_filter = ('has_subtype', 'impact_group')
    list_editable = ('order',)
    model = ImpactType
