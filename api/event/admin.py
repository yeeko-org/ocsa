from django.contrib import admin
from django.contrib.admin import AdminSite, register

from .models import EventType, EventGroup


@register(EventType, EventGroup)
class EventAdmin(admin.ModelAdmin):
    pass

