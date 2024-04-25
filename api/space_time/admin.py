from django.contrib import admin

from space_time.models import Ubicacion, CatTemporalidad, Temporalidad


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    pass


@admin.register(CatTemporalidad)
class CatTemporalidadAdmin(admin.ModelAdmin):
    pass


@admin.register(Temporalidad)
class TemporalidadAdmin(admin.ModelAdmin):
    pass
