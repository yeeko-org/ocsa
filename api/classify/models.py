from django.db import models

from work_flux.models import StatusControl


POSITION_CHOICES = (
    ('support', 'A favor'),
    ('oppose', 'En contra'),
    ('neutral', 'Neutral'),
    ('other', 'Otro'),
    ('undefined', 'Indefinido'),
)


class ParticipantGroup(models.Model):

    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Tipo de Participante'
        verbose_name_plural = 'Tipos de Participantes'


class ParticipantType(models.Model):

    name = models.CharField(max_length=255)
    position = models.CharField(
        max_length=14, choices=POSITION_CHOICES, default='undefined')
    participant_group = models.ForeignKey(
        ParticipantGroup, on_delete=models.CASCADE,
        blank=True, null=True, related_name='participant_types')
    required_interests = models.BooleanField(
        default=True, verbose_name='Se requerirá que se agreguen intereses')
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Subtipo de Participación en Proyecto'
        verbose_name_plural = 'Subtipo de Participación en Proyecto'


class Belong(models.Model):
    short_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'short_name']
        verbose_name = 'Grupo de Pertenencia (Vulnerabilidad)'
        verbose_name_plural = 'Grupos de Pertenencia (Vulnerabilidades)'


class IndigenousGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Indígena'
        ordering = ['name']
        verbose_name_plural = 'Grupos Indígenas'


CAPITAL_TYPES = (
    ('public', 'Público'),
    ('private', 'Privado'),
    ('mixed', 'Mixto'),
    ("conflict", "Conflicto"),
)


class SectorGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_collective = models.BooleanField(blank=True, null=True)
    has_belongs = models.BooleanField(default=True)
    capital_type = models.CharField(
        max_length=10, choices=CAPITAL_TYPES, blank=True, null=True)
    icon = models.CharField(max_length=90, blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    order = models.SmallIntegerField(default=10)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Grupo Sectorial'
        verbose_name_plural = 'Grupos Sectoriales'


class Sector(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sector_group = models.ForeignKey(
        SectorGroup, on_delete=models.CASCADE, related_name='sectors')
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=50)

    def __str__(self):
        return self.name or 'Sin nombre'

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'


class InterestGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)
    icon = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Agrupador de tipos de interés'
        verbose_name_plural = 'Agrupadores de tipos de interés'


class InterestType(models.Model):

    interest_group = models.ForeignKey(
        InterestGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # participant_types = models.ManyToManyField(
    #     ParticipantType, blank=True, related_name='interest_types')
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Tipo de interés'
        verbose_name_plural = 'Tipos de interés'


class InterestSubtype(models.Model):
    interest_type = models.ForeignKey(
        InterestType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Subtipo de interés'
        verbose_name_plural = 'Subtipos de interés'


class Country(models.Model):
    name = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = 'Pais'
        verbose_name_plural = 'Paises'
