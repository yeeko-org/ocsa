from django.contrib import admin
from event.models import (
    HechosViolencia, FormaHechoViolencia, Violencia, FormaAC, SubformaAC,
    AccionesColectivas, GruposApoyo, OpositoresToAC, SectorSocial, CondicionMujerVictima)


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


@admin.register(AccionesColectivas)
class AccionesColectivaAdmin(admin.ModelAdmin):
    pass


@admin.register(GruposApoyo)
class GruposApoyoAdmin(admin.ModelAdmin):
    pass


@admin.register(OpositoresToAC)
class OpositoresToACAdmin(admin.ModelAdmin):
    pass


@admin.register(CondicionMujerVictima)
class CondicionMujerVictimaAdmin(admin.ModelAdmin):
    pass


@admin.register(SectorSocial)
class SectorSocialAdmin(admin.ModelAdmin):
    pass
