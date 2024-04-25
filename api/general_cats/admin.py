from django.contrib import admin

from general_cats.models import CondicionMujerVictima, SectorSocial


@admin.register(CondicionMujerVictima)
class CondicionMujerVictimaAdmin(admin.ModelAdmin):
    pass


@admin.register(SectorSocial)
class SectorSocialAdmin(admin.ModelAdmin):
    pass
