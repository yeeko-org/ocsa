from django.contrib import admin

from .models import (
    AccionesColectivas, AfectacionEcologica, AfectacionSocial, Capital,
    CatTemporalidad, CondicionMujerVictima, CSA, Estado, EstatusProyecto,
    EstatusProyectos, FormaAC, FormaHechoViolencia, FormaOrganizacion,
    GruposApoyo, HechosViolencia, InteresesOpositores, InteresesPoblacion,
    Mujer, Nota, Opositores, OpositoresToAC, Otros, PoblacionAfectada,
    CatPoblacionAfectada, Proyecto, RegistroNotas, SectorSocial, SubformaAC,
    CatSubpoblacionAfectada, Temporalidad, TipoAfectacionEcologica,
    TipoAfectacionSocial, TipoDespliegueCapital, TipoMegaproyecto,
    Ubicacion, Violencia, OpositorToProyecto, OpositorToNotas,
    OpositorToUbicaciones, AfectacionEcologicaToUbicacion,
    AfectacionSocialToUbicacion, ViolenciaToOpositor, ViolenciaToUbicacion,
    AccionColectivaToUbicacion
)

# ---------------------------------Space Time---------------------------------


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    pass


@admin.register(CatTemporalidad)
class CatTemporalidadAdmin(admin.ModelAdmin):
    pass


@admin.register(Temporalidad)
class TemporalidadAdmin(admin.ModelAdmin):
    pass


# ----------------------------------Projec-----------------------------------


@admin.register(CSA)
class CSAAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoDespliegueCapital)
class TipoDespliegueCapitalAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoMegaproyecto)
class TipoMegaproyectoAdmin(admin.ModelAdmin):
    pass


@admin.register(EstatusProyecto)
class EstatusProyectoAdmin(admin.ModelAdmin):
    pass


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    pass


@admin.register(EstatusProyectos)
class EstatusProyectosAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Source-----------------------------------


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    pass


@admin.register(RegistroNotas)
class RegistroNotasAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Actor-----------------------------------


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


@admin.register(CatPoblacionAfectada)
class PoblacionesAfectadasAdmin(admin.ModelAdmin):
    pass


@admin.register(CatSubpoblacionAfectada)
class SubpoblacionAfectadaAdmin(admin.ModelAdmin):
    pass


@admin.register(GruposApoyo)
class GruposApoyoAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Impact-----------------------------------


@admin.register(AfectacionEcologica)
class AfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoAfectacionEcologica)
class TipoAfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@admin.register(AfectacionSocial)
class AfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@admin.register(TipoAfectacionSocial)
class TipoAfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@admin.register(Otros)
class OtrosAdmin(admin.ModelAdmin):
    pass


# -----------------------------------event-----------------------------------


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


@admin.register(OpositoresToAC)
class OpositoresToACAdmin(admin.ModelAdmin):
    pass


@admin.register(CondicionMujerVictima)
class CondicionMujerVictimaAdmin(admin.ModelAdmin):
    pass


@admin.register(SectorSocial)
class SectorSocialAdmin(admin.ModelAdmin):
    pass


@admin.register(OpositorToProyecto)
class OpositorToProyectoAdmin(admin.ModelAdmin):
    pass


@admin.register(OpositorToNotas)
class OpositorToNotasAdmin(admin.ModelAdmin):
    pass


@admin.register(OpositorToUbicaciones)
class OpositorToUbicacionesAdmin(admin.ModelAdmin):
    pass


@admin.register(AfectacionEcologicaToUbicacion)
class AfectacionEcologicaToUbicacionAdmin(admin.ModelAdmin):
    pass


@admin.register(AfectacionSocialToUbicacion)
class AfectacionSocialToUbicacionAdmin(admin.ModelAdmin):
    pass


@admin.register(ViolenciaToOpositor)
class ViolenciaToOpositorAdmin(admin.ModelAdmin):
    pass


@admin.register(ViolenciaToUbicacion)
class ViolenciaToUbicacionAdmin(admin.ModelAdmin):
    pass


@admin.register(AccionColectivaToUbicacion)
class AccionColectivaToUbicacionAdmin(admin.ModelAdmin):
    pass
