from django.contrib import admin


from others.models import Otros


@admin.register(Otros)
class OtrosAdmin(admin.ModelAdmin):
    pass
