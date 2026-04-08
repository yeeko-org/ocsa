from django.db import models
from source.models import Mention
from actor.models import Participant
# from work_flux.models import StatusControl
from utils.mix_models import CatalogGroup, CatalogType


class EventGroup(CatalogGroup):
    model_origin = models.CharField(
        max_length=80, blank=True, null=True)
    is_conflict_related = models.BooleanField(default=False)
    show_position = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'Grupo de Evento'
        verbose_name_plural = 'Grupos de Eventos'


class EventType(CatalogType):
    purpose_defense = models.TextField(
        blank=True, null=True,
        verbose_name="Explicación del mecanismo legal de defensa")
    purpose_spoliation = models.TextField(
        blank=True, null=True,
        verbose_name="Explicación del mecanismo legal de despojo")
    event_group = models.ForeignKey(
        EventGroup, on_delete=models.CASCADE, related_name='event_types')
    has_displacement = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'
        ordering = ['order']


class EventSubtype(CatalogType):
    event_types = models.ManyToManyField(
        EventType, blank=True, related_name='event_subtypes')

    class Meta:
        ordering = ['order']
        verbose_name = 'Subtipo de Evento'
        verbose_name_plural = 'Subtipos de Eventos'


class Purpose(CatalogGroup):
    short_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Propósito de Evento'
        verbose_name_plural = 'Propósitos de Eventos'


class Event(models.Model):
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, related_name='events')
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE, related_name='events')
    date = models.DateField(blank=True, null=True)
    number_women = models.IntegerField(blank=True, null=True)
    number_men = models.IntegerField(blank=True, null=True)
    number_mix = models.IntegerField(blank=True, null=True)
    purpose = models.ForeignKey(
        Purpose, on_delete=models.CASCADE, blank=True, null=True,
        related_name='events')

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.mention)

    class Meta:
        ordering = ["event_type__event_group__order", "event_type__order", "id"]
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'


class InvolvedRole(CatalogType):
    pass

    class Meta:
        ordering = ['order']
        verbose_name = 'Rol en Actividad'
        verbose_name_plural = 'Roles en Actividades'


class Involved(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='involvements')
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='involvements')
    involved_role = models.ForeignKey(
        InvolvedRole, on_delete=models.CASCADE, blank=True, null=True)
    number_women = models.IntegerField(blank=True, null=True)
    number_men = models.IntegerField(blank=True, null=True)
    number_mix = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.event} - {self.participant}"

    class Meta:
        verbose_name = 'Involucrado en Evento'
        verbose_name_plural = 'Involucrados en Eventos'
