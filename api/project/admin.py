from django.contrib import admin
from .models import Project, MegaprojectType, DeploymentCapitalType


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


class DeploymentCapitalTypeInline(admin.TabularInline):
    model = DeploymentCapitalType
    extra = 0


@admin.register(MegaprojectType)
class MegaprojectTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'has_many_dct')
