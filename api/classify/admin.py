from django.contrib import admin
from classify.models import Sector
from django.contrib.admin import AdminSite, register


@register(Sector)
class ClassifyAdmin(admin.ModelAdmin):
    pass

