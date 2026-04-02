from django.contrib import admin
from django.contrib.admin import register
from ps_schema.models import Collection


@register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('snake_name', 'level', 'order', 'icon', 'color')
    list_editable = ('order', 'icon', 'color')
    list_filter = ('level',)