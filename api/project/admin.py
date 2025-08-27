from django.contrib import admin
from .models import Project, MegaprojectType, ExtractivismType


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(ExtractivismType)
class ExtractivismTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'ai_name')
    list_editable = ('ai_name', 'order')


class ExtractivismTypeInline(admin.TabularInline):
    model = ExtractivismType
    extra = 0


@admin.register(MegaprojectType)
class MegaprojectTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
