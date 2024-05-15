from django.contrib import admin
from space_time.models import Country, Locality, Municipality, State


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag_emoji')


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'municipality_id', 'population',
                    'latitude', 'longitude', 'altitude')
    raw_id_fields = ('municipality',)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state_id', 'population')
    raw_id_fields = ('state',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'inegi_code')
