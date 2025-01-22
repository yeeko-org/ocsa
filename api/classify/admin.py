from django.contrib import admin
from classify.models import Sector, ParticipantType
from django.contrib.admin import AdminSite, register


@register(Sector, ParticipantType)
class ClassifyAdmin(admin.ModelAdmin):
    pass
