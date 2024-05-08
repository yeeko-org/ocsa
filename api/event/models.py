from django.db import models
from source.models import Mention
from actor.models import Participant
from work_flux.models import StatusControl


class EventGroup(models.Model):
    name = models.CharField(max_length=255)
    model_origin = models.CharField(
        max_length=80, blank=True, null=True)


class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    group = models.ForeignKey(
        EventGroup, on_delete=models.CASCADE, blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'


class EventSubtype(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    event_types = models.ManyToManyField(EventType, blank=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subtipo de Evento'
        verbose_name_plural = 'Subtipos de Eventos'


class Event(models.Model):
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, blank=True, null=True)
    event_subtype = models.ForeignKey(
        EventSubtype, on_delete=models.CASCADE, blank=True, null=True)
    # RICK: Temporal, hasta que no existan ya conflictos
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.mention

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'


init_event_roles = [
    "Victimario",
    "Responsable",
    "Víctima"]


class EventRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Rol en Evento'
        verbose_name_plural = 'Roles en Eventos'


class Involved(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    event_role = models.ForeignKey(
        EventRole, on_delete=models.CASCADE, blank=True, null=True)
    number_women = models.IntegerField(blank=True, null=True)
    number_men = models.IntegerField(blank=True, null=True)
    number_mix = models.IntegerField(blank=True, null=True)


