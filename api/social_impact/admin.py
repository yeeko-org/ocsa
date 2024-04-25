from django.contrib import admin

from social_impact.models import AfectacionesSociales, TipoAfectacionesSociales


@admin.register(AfectacionesSociales)
class AfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoAfectacionesSociales)
class TipoAfectacionesSocialesAdmin(admin.ModelAdmin):
    pass
