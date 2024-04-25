from django.contrib import admin
from source.models import (Nota, RegistroNotas)


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    pass


@admin.register(RegistroNotas)
class RegistroNotasAdmin(admin.ModelAdmin):
    pass
