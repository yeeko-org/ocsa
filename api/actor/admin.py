from django.contrib import admin
from .models import OriginReference, Actor


@admin.register(OriginReference)
class OriginReferenceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'actor', 'type_model', 'field_name', 'origin_id',
        'actor_created', 'created_at'
    )
    raw_id_fields = ('actor',)
    search_fields = ('actor__name', 'origin_id')
    list_filter = ('type_model', 'field_name', 'actor_created')


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'alternative_names', 'parent_actor', 'sector')
    search_fields = ('name', 'alternative_names')
    list_filter = ('sector__sector_group', 'countries', 'indigenous_group')
