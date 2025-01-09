from django.contrib import admin
from django.contrib.admin import AdminSite, register

from .models import EventSubtype, EventType, EventGroup


@register(EventSubtype, EventType, EventGroup)
class EventAdmin(admin.ModelAdmin):
    pass

