from django.db import models
from event.models import Event
from impact.models import Impact
from work_flux.models import StatusControl, CommentsMixin
from classify.models import Country
from space_time.models import State, Municipality, Locality


class Dimension(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)
    show_countries = models.BooleanField(default=False)
    show_states = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Dimensión del desplazamiento'
        verbose_name_plural = 'Dimensiones de desplazamientos'


class PopulationSize(CommentsMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Población afectada por desplazamiento'
        verbose_name_plural = 'Poblaciones afectadas por desplazamiento'


class Temporality(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Temporalidad del desplazamiento'
        verbose_name_plural = 'Temporalidades de desplazamientos'


class Displacement(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacements')
    impact = models.ForeignKey(
        Impact, on_delete=models.CASCADE, blank=True, null=True,
        related_name='displacements')
    dimension = models.ForeignKey(
        Dimension, on_delete=models.CASCADE, blank=True, null=True)
    population_size = models.ForeignKey(
        PopulationSize, on_delete=models.CASCADE, blank=True, null=True)
    temporality = models.ForeignKey(
        Temporality, on_delete=models.CASCADE, blank=True, null=True)
    rithm = models.CharField(max_length=255, blank=True, null=True)
    origin_state = models.ForeignKey(
        State, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_origin')
    origin_municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_origin')
    origin_locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_origin')
    destination_country = models.ForeignKey(
        Country, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_destination')
    destination_state = models.ForeignKey(
        State, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_destination')
    destination_municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_destination')
    destination_locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE,
        blank=True, null=True, related_name='displacement_destination')


    def __str__(self):
        return f"{self.event or self.impact}"

    class Meta:
        verbose_name = 'Desplazamiento forzado'
        verbose_name_plural = 'Desplazamientos forzados'

