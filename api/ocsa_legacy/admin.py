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


@register(Ubicacion, CatTemporalidad, Temporalidad, site=legacy_admin_site)
class LegacySpaceTimeAdmin(admin.ModelAdmin):
    pass


# ----------------------------------Project-----------------------------------


@register(
    CSA, TipoDespliegueCapital, TipoMegaproyecto, EstatusProyecto, Proyecto,
    EstatusProyectos, site=legacy_admin_site
)
class LegacyProjectAdmin(admin.ModelAdmin):
    pass


@register(Nota, RegistroNotas, site=legacy_admin_site)
class LegacySourceAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Actor-----------------------------------


@register(Capital, site=legacy_admin_site)
class LegacyCapitalAdmin(admin.ModelAdmin):
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


@register(
    Estado, FormaOrganizacion, InteresesOpositores, InteresesPoblacion,
    Mujer, Opositores, PoblacionAfectada, CatPoblacionAfectada,
    CatSubpoblacionAfectada, GruposApoyo, site=legacy_admin_site
)
class LegacyActorAdmin(admin.ModelAdmin):
    pass


# -----------------------------------Impact-----------------------------------


@register(
    AfectacionEcologica, TipoAfectacionEcologica, AfectacionSocial,
    TipoAfectacionSocial, Otros, site=legacy_admin_site
)
class LegacyImpactAdmin(admin.ModelAdmin):
    pass


@register(
    HechosViolencia, FormaHechoViolencia, Violencia, FormaAC, SubformaAC,
    AccionesColectivas, OpositoresToAC, CondicionMujerVictima, SectorSocial,
    OpositorToProyecto, OpositorToNotas, OpositorToUbicaciones,
    AfectacionEcologicaToUbicacion, AfectacionSocialToUbicacion,
    ViolenciaToOpositor, ViolenciaToUbicacion, AccionColectivaToUbicacion,
    site=legacy_admin_site
)
class LegacyEventAdmin(admin.ModelAdmin):
    pass
