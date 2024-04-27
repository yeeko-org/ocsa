from django.db import models

from source.models import Mention


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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'


class Event(models.Model):
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, blank=True, null=True)
