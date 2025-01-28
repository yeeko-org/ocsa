from django.db import models
from source.models import Mention
from actor.models import Participant
from work_flux.models import StatusControl
# from impact.models import Impact
# from space_time.models import Location


class EventGroup(models.Model):
    name = models.CharField(max_length=255)
    model_origin = models.CharField(
        max_length=80, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=2)
    color = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Grupo de Evento'
        verbose_name_plural = 'Grupos de Eventos'


class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    event_group = models.ForeignKey(EventGroup, on_delete=models.CASCADE)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=20)
    has_displacement = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'


class EventSubtype(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    event_types = models.ManyToManyField(
        EventType, blank=True, related_name='event_subtypes')
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Subtipo de Evento'
        verbose_name_plural = 'Subtipos de Eventos'


class Event(models.Model):
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, blank=True, null=True,
        related_name='events')
    # RICK: Temporal, hasta que no existan ya conflictos
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE, blank=True, null=True,
        related_name='events')
    event_subtype = models.ForeignKey(
        EventSubtype, on_delete=models.CASCADE, blank=True, null=True,
        related_name='events')
    date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    number_women = models.IntegerField(blank=True, null=True)
    number_men = models.IntegerField(blank=True, null=True)
    number_mix = models.IntegerField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.mention)

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'


class InvolvedRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Rol en Actividad'
        verbose_name_plural = 'Roles en Actividades'


class Involved(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='involvements')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
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


# class Displacement(models.Model):
#     event = models.ForeignKey(
#         Event, on_delete=models.CASCADE,
#         blank=True, null=True, related_name='displacements')
#     impact = models.ForeignKey(
#         Impact, on_delete=models.CASCADE, blank=True, null=True,
#         related_name='displacements')
#     # massive_type = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.event} - {self.participant}"
#
#     class Meta:
#         verbose_name = 'Desplazamiento forzado'
#         verbose_name_plural = 'Desplazamientos forzados'


# class EventLocation(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     location = models.ForeignKey(
#         Location, on_delete=models.CASCADE)
#     status_location = models.ForeignKey(
#         StatusControl, on_delete=models.CASCADE, blank=True, null=True)
#
#     def __str__(self):
#         return self.location
#
#     class Meta:
#         verbose_name = 'Ubicación de Evento'
#         verbose_name_plural = 'Ubicaciones de Eventos'
