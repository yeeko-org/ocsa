from django.contrib import admin

from actors.models import (
    Capital, Estado, FormaOrganizacion, InteresesOpositores,
    InteresesPoblacion, Mujer, Opositor, PoblacionAfectada,
    PoblacionesAfectadas, SubpoblacionAfectada
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


@admin.register(Opositor)
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
