from django.contrib import admin
from classify.models import Sector, ParticipantType
from django.contrib.admin import AdminSite, register


@register(Sector)
class ClassifyAdmin(admin.ModelAdmin):
    pass


@register(ParticipantType)
class ParticipantTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order', 'position')
