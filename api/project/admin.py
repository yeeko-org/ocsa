from django.contrib import admin
from .models import Project, MegaprojectType, ExtractivismType


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


class ExtractivismTypeInline(admin.TabularInline):
    model = ExtractivismType
    extra = 0


@admin.register(MegaprojectType)
class MegaprojectTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'has_many_dct')
