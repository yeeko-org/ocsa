from django.contrib import admin
from .models import OriginReference


@admin.register(OriginReference)
class OriginReferenceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'actor', 'type_model', 'field_name', 'origin_id',
        'actor_created', 'created_at'
    )
    raw_id_fields = ('actor',)
    search_fields = ('actor__name','actor__id', 'origin_id')
    list_filter = ('type_model', 'field_name', 'actor_created')
