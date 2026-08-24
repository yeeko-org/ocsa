from django.contrib import admin
from .models import Project, MegaprojectType, ExtractivismType


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # status_location se deriva de las ubicaciones (adr-0027)
    readonly_fields = ['status_location']


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
