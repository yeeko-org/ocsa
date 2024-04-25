from django.contrib import admin

from tempo_extend.models import CatTemporalidad, Temporalidad


@admin.register(CatTemporalidad)
class CatTemporalidadAdmin(admin.ModelAdmin):
    pass


@admin.register(Temporalidad)
class TemporalidadAdmin(admin.ModelAdmin):
    pass
