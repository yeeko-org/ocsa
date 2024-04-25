from django.contrib import admin

from impact.models import AfectacionesEcologicas, TipoAfectacionesEcologicas, TipoAfectacionesSociales, \
    AfectacionesSociales, Otros


@admin.register(AfectacionesEcologicas)
class AfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoAfectacionesEcologicas)
class TipoAfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@admin.register(AfectacionesSociales)
class AfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoAfectacionesSociales)
class TipoAfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@admin.register(Otros)
class OtrosAdmin(admin.ModelAdmin):
    pass
