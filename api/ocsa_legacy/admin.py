from django.contrib import admin
from django.contrib.admin import AdminSite, register

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


class LegacyAdminSite(AdminSite):
    site_header = "Legacy Admin"
    site_title = "Legacy OCSA Admin Portal"
    index_title = "Welcome to Legacy OCSA Portal"


legacy_admin_site = LegacyAdminSite(name='legacy_admin')


@register(Ubicacion, site=legacy_admin_site)
class UbicacionAdmin(admin.ModelAdmin):
    pass


@register(CatTemporalidad, site=legacy_admin_site)
class CatTemporalidadAdmin(admin.ModelAdmin):
    pass


@register(Temporalidad, site=legacy_admin_site)
class TemporalidadAdmin(admin.ModelAdmin):
    pass


# ----------------------------------Projec-----------------------------------


@register(CSA, site=legacy_admin_site)
class CSAAdmin(admin.ModelAdmin):
    pass


@register(TipoDespliegueCapital, site=legacy_admin_site)
class TipoDespliegueCapitalAdmin(admin.ModelAdmin):
    pass


@register(TipoMegaproyecto, site=legacy_admin_site)
class TipoMegaproyectoAdmin(admin.ModelAdmin):
    pass


@register(EstatusProyecto, site=legacy_admin_site)
class EstatusProyectoAdmin(admin.ModelAdmin):
    pass


@register(Proyecto, site=legacy_admin_site)
class ProyectoAdmin(admin.ModelAdmin):
    pass


@register(EstatusProyectos, site=legacy_admin_site)
class EstatusProyectosAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Source-----------------------------------


@register(Nota, site=legacy_admin_site)
class NotaAdmin(admin.ModelAdmin):
    pass


@register(RegistroNotas, site=legacy_admin_site)
class RegistroNotasAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Actor-----------------------------------


@register(Capital, site=legacy_admin_site)
class CapitalAdmin(admin.ModelAdmin):
    readonly_fields = ["proyecto", "nota"]
    list_display = [
        "id",
        "nombre",
        "matriz",
        "filial",
        "directores",
        "inversionistas",
        "nacionalidad",
        "interes",
    ]


@register(Estado, site=legacy_admin_site)
class EstadoAdmin(admin.ModelAdmin):
    pass


@register(FormaOrganizacion, site=legacy_admin_site)
class FormaOrganizacionAdmin(admin.ModelAdmin):
    pass


@register(InteresesOpositores, site=legacy_admin_site)
class InteresesOpositoresAdmin(admin.ModelAdmin):
    pass


@register(InteresesPoblacion, site=legacy_admin_site)
class InteresesPoblacionAdmin(admin.ModelAdmin):
    pass


@register(Mujer, site=legacy_admin_site)
class MujerAdmin(admin.ModelAdmin):
    pass


@register(Opositores, site=legacy_admin_site)
class OpositorAdmin(admin.ModelAdmin):
    pass


@register(PoblacionAfectada, site=legacy_admin_site)
class PoblacionAfectadaAdmin(admin.ModelAdmin):
    pass


@register(CatPoblacionAfectada, site=legacy_admin_site)
class PoblacionesAfectadasAdmin(admin.ModelAdmin):
    pass


@register(CatSubpoblacionAfectada, site=legacy_admin_site)
class SubpoblacionAfectadaAdmin(admin.ModelAdmin):
    pass


@register(GruposApoyo, site=legacy_admin_site)
class GruposApoyoAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Impact-----------------------------------


@register(AfectacionEcologica, site=legacy_admin_site)
class AfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@register(TipoAfectacionEcologica, site=legacy_admin_site)
class TipoAfectacionesEcologicasAdmin(admin.ModelAdmin):
    pass


@register(AfectacionSocial, site=legacy_admin_site)
class AfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@register(TipoAfectacionSocial, site=legacy_admin_site)
class TipoAfectacionesSocialesAdmin(admin.ModelAdmin):
    pass


@register(Otros, site=legacy_admin_site)
class OtrosAdmin(admin.ModelAdmin):
    pass


# -----------------------------------event-----------------------------------


@register(HechosViolencia, site=legacy_admin_site)
class HechosViolenciaAdmin(admin.ModelAdmin):
    pass


@register(FormaHechoViolencia, site=legacy_admin_site)
class FormaHechoViolenciaAdmin(admin.ModelAdmin):
    pass


@register(Violencia, site=legacy_admin_site)
class ViolenciaAdmin(admin.ModelAdmin):
    pass


@register(FormaAC, site=legacy_admin_site)
class FormaACAdmin(admin.ModelAdmin):
    pass


@register(SubformaAC, site=legacy_admin_site)
class SubformaACAdmin(admin.ModelAdmin):
    pass


@register(AccionesColectivas, site=legacy_admin_site)
class AccionesColectivaAdmin(admin.ModelAdmin):
    pass


@register(OpositoresToAC, site=legacy_admin_site)
class OpositoresToACAdmin(admin.ModelAdmin):
    pass


@register(CondicionMujerVictima, site=legacy_admin_site)
class CondicionMujerVictimaAdmin(admin.ModelAdmin):
    pass


@register(SectorSocial, site=legacy_admin_site)
class SectorSocialAdmin(admin.ModelAdmin):
    pass


@register(OpositorToProyecto, site=legacy_admin_site)
class OpositorToProyectoAdmin(admin.ModelAdmin):
    pass


@register(OpositorToNotas, site=legacy_admin_site)
class OpositorToNotasAdmin(admin.ModelAdmin):
    pass


@register(OpositorToUbicaciones, site=legacy_admin_site)
class OpositorToUbicacionesAdmin(admin.ModelAdmin):
    pass


@register(AfectacionEcologicaToUbicacion, site=legacy_admin_site)
class AfectacionEcologicaToUbicacionAdmin(admin.ModelAdmin):
    pass


@register(AfectacionSocialToUbicacion, site=legacy_admin_site)
class AfectacionSocialToUbicacionAdmin(admin.ModelAdmin):
    pass


@register(ViolenciaToOpositor, site=legacy_admin_site)
class ViolenciaToOpositorAdmin(admin.ModelAdmin):
    pass


@register(ViolenciaToUbicacion, site=legacy_admin_site)
class ViolenciaToUbicacionAdmin(admin.ModelAdmin):
    pass


@register(AccionColectivaToUbicacion, site=legacy_admin_site)
class AccionColectivaToUbicacionAdmin(admin.ModelAdmin):
    pass
