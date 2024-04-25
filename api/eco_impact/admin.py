from django.contrib import admin

from eco_impact.models import AfectacionesEcologicas, TipoAfectacionesEcologicas


@admin.register(AfectacionesEcologicas)
class AfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoAfectacionesEcologicas)
class TipoAfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass
