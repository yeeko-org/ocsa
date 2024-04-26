from django.contrib import admin

from actor.models import (
    Capital, Estado, FormaOrganizacion, InteresesOpositores,
    InteresesPoblacion, Mujer, Opositores, PoblacionAfectada,
    PoblacionesAfectadas, SubpoblacionAfectada, GruposApoyo
)


@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    pass


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    pass


@admin.register(FormaOrganizacion)
class FormaOrganizacionAdmin(admin.ModelAdmin):
    pass


@admin.register(InteresesOpositores)
class InteresesOpositoresAdmin(admin.ModelAdmin):
    pass


@admin.register(InteresesPoblacion)
class InteresesPoblacionAdmin(admin.ModelAdmin):
    pass


@admin.register(Mujer)
class MujerAdmin(admin.ModelAdmin):
    pass


@admin.register(Opositores)
class OpositorAdmin(admin.ModelAdmin):
    pass


@admin.register(PoblacionAfectada)
class PoblacionAfectadaAdmin(admin.ModelAdmin):
    pass


@admin.register(PoblacionesAfectadas)
class PoblacionesAfectadasAdmin(admin.ModelAdmin):
    pass


@admin.register(SubpoblacionAfectada)
class SubpoblacionAfectadaAdmin(admin.ModelAdmin):
    pass


@admin.register(GruposApoyo)
class GruposApoyoAdmin(admin.ModelAdmin):
    pass
