from django.db import models

from source.models import Mention
from space_time.models import Country
from django.db.models import JSONField
from work_flux.models import StatusControl, CommentsMixin
from classify.models import (
    ParticipantType, Belong, IndigenousGroup, Sector, InterestType)
# from work_flux.models import StatusRegister


def default_list():
    return []


# Tablas origen: Capital, Estado, Opositores, Poblaciones, GruposApoyo
class Actor(CommentsMixin, models.Model):
    GEO_REACH_CHOICES = (
        ('local', 'Local'),
        ('regional', 'Regional'),
        ('national', 'Nacional'),
        ('international', 'Internacional'),
        ('global', 'Global'),
    )

    SEX_CHOICES = (
        ('man', 'Hombre'),
        ('woman', 'Mujer'),
    )

    # El nombre viene del campo "nombre", excepto:
    # Estado, que tiene 3 campos y su comportamiento se explica arrriba
    name = models.CharField(max_length=255)
    official_name = models.CharField(
        max_length=255, blank=True, null=True)
    std_name = models.CharField(
        max_length=255, blank=True, null=True)
    alternative_names = models.JSONField(
        default=default_list, blank=True, null=True)
    is_incomplete = models.BooleanField(default=False)
    is_name_created = models.BooleanField(default=False)

    parent_actor = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children_actors', verbose_name='Actor padre')
    others_parents = models.ManyToManyField(
        'self', blank=True, verbose_name='Otros padres')
    network_seq = models.IntegerField(blank=True, null=True)
    is_only_related = models.BooleanField(
        blank=True, null=True, verbose_name='Se creó solo por relación')

    # Capital.nacionalidad
    countries = models.ManyToManyField(Country, blank=True)
    sector = models.ForeignKey(
        Sector, on_delete=models.CASCADE, blank=True, null=True)
    sector_name = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='Nombre del sector (opcional)')
    geo_reach = models.CharField(
        max_length=15, choices=GEO_REACH_CHOICES, blank=True, null=True)
    belongs = models.ManyToManyField(Belong, blank=True)
    indigenous_group = models.ForeignKey(
        IndigenousGroup, on_delete=models.CASCADE, blank=True, null=True)

    capital_extension = JSONField(blank=True, null=True)
    # True cuando Opositor.mujer tiene valor y su id es mayor o igual a 2
    sex = models.CharField(
        max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    capital_id_ref = models.IntegerField(blank=True, null=True)

    # def add_comment(self, comment: str):
    #     if not comment:
    #         return
    #     if self.comments:
    #         if comment not in self.comments:
    #             self.comments += f"\n\n{comment}"
    #     else:
    #         self.comments = comment
    #     self.save()

    status_validation_id: str | None

    def append_alternative_name(self, name, save=True):
        if not name or self.name == name:
            return

        if not isinstance(self.alternative_names, list):
            self.alternative_names = []

        if name not in self.alternative_names:
            self.alternative_names.append(name)
            if save:
                self.save()

    def get_participant_count(self):
        return Participant.objects.filter(actor=self).count()

    def get_sector_group(self):
        return self.sector.sector_group_id if self.sector else None  # type: ignore

    def __str__(self):
        return self.official_name or self.name

    class Meta:
        verbose_name = 'Actor'
        verbose_name_plural = 'Actores'


MEMBERSHIP_TYPES = (
    ('director', 'Director'),
    ('investor', 'Inversionista'),
    ('chief_executive', 'Director Ejecutivo'),
    ('other', 'Otro directivo'),
    ('member', 'Integrante'),
)


class Member(models.Model):
    actor_individual = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name='actor_individual')
    actor_collective = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name='actor_collective')
    membership_type = models.CharField(
        max_length=20, choices=MEMBERSHIP_TYPES, default='member')

    def __str__(self):
        return f"{self.actor_individual} - {self.actor_collective}"

    class Meta:
        verbose_name = 'Persona integrante de actor colectivo'
        verbose_name_plural = 'Personas integrantes de actor colectivo'


class Participant(models.Model):
    actor = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name='participants')
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, related_name='participants')
    participant_types = models.ManyToManyField(ParticipantType, blank=True)
    # raw_interests = models.TextField(
    #     blank=True, null=True, verbose_name='Intereses (extensión)')

    def __str__(self):
        return self.actor

    class Meta:
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'


# En algunos casos, esto provendrá de una relación 1:1, a veces M:1,
# pero vamos a estandarizar siempre a M:1 a través de Interest
# Los campos origen de Actor tienen esto:
# Capital.interes, PoblacionesAfectadas.interes, GruposApoyo.interes
# Opositores a través de InteresesOpositores (m:m), parece algo complejo!!
# Estado no tiene interés

class Interest(models.Model):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='interests')
    interest_type = models.ForeignKey(
        InterestType, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()

    def __str__(self):
        return self.text or str(self.pk)

    class Meta:
        verbose_name = 'Interés'
        verbose_name_plural = 'Intereses'


LEGACY_MODELS = (
    ('Capital', 'Capital'),
    ('Estado', 'Estado'),
    ('Opositores', 'Opositores'),
    ('PoblacionesAfectadas', 'PoblacionesAfectadas'),
    ('GruposApoyo', 'GruposApoyo'),
)


class OriginReference(models.Model):
    actor = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name='origin_references')
    type_model = models.CharField(max_length=20, choices=LEGACY_MODELS)
    field_name = models.CharField(max_length=255, blank=True, null=True)
    origin_id = models.IntegerField()
    actor_created = models.BooleanField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin_id} - {self.type_model}"

    class Meta:
        verbose_name = 'Referencia de Origen'
        verbose_name_plural = 'Referencias de Origen'
