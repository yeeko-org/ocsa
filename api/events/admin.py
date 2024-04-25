from django.contrib import admin
from events.models import (
    HechosViolencia, FormaHechoViolencia, Violencia, FormaAC, SubformaAC,
    AccioneColectiva, GruposApoyo, OpositoresToAC)


@admin.register(HechosViolencia)
class HechosViolenciaAdmin(admin.ModelAdmin):
    pass


@admin.register(FormaHechoViolencia)
class FormaHechoViolenciaAdmin(admin.ModelAdmin):
    pass


@admin.register(Violencia)
class ViolenciaAdmin(admin.ModelAdmin):
    pass


@admin.register(FormaAC)
class FormaACAdmin(admin.ModelAdmin):
    pass


@admin.register(SubformaAC)
class SubformaACAdmin(admin.ModelAdmin):
    pass


@admin.register(AccioneColectiva)
class AccioneColectivaAdmin(admin.ModelAdmin):
    pass


@admin.register(GruposApoyo)
class GruposApoyoAdmin(admin.ModelAdmin):
    pass


@admin.register(OpositoresToAC)
class OpositoresToACAdmin(admin.ModelAdmin):
    pass
