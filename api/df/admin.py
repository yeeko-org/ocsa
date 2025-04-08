from django.contrib import admin
from df.models import Displacement, Dimension, PopulationSize, Temporality
from django.contrib.admin import register


@register(Displacement, Dimension, PopulationSize, Temporality)
class DfAdmin(admin.ModelAdmin):
    pass
