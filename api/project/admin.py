from django.contrib import admin
from project.models import (CSA, TipoDespliegueCapital,
                            TipoMegaproyecto, EstatusProyecto, Proyecto, EstatusProyectos)


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
