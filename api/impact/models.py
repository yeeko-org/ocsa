from django.db import models
from source.models import Mention
from work_flux.models import StatusControl


class ImpactGroup(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_social = models.BooleanField(default=True)
    show_position = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo de Afectaciones'
        verbose_name_plural = 'Grupos de Afectaciones'


class ImpactType(models.Model):
    name = models.CharField(max_length=255)
    impact_group = models.ForeignKey(ImpactGroup, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    short_name = models.CharField(
        max_length=50, blank=True, null=True, help_text='Nombre corto')
    # is_social = models.BooleanField(default=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=0)
    has_displacement = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Tipo de Afectación'
        verbose_name_plural = 'Tipos de Afectaciones'


class ImpactSubtype(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    impact_type = models.ForeignKey(
        ImpactType, on_delete=models.CASCADE, related_name='impact_subtypes')
    help_text = models.TextField(blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Subtipo de Afectación'
        verbose_name_plural = 'Subtipos de Afectaciones'


class Impact(models.Model):
    impact_type = models.ForeignKey(
        ImpactType, on_delete=models.CASCADE)
    impact_subtype = models.ForeignKey(
        ImpactSubtype, on_delete=models.CASCADE, blank=True, null=True)
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, related_name='impacts')
    description = models.TextField(blank=True, null=True)
    is_potential = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f'{self.impact_type} - {self.mention}'

    class Meta:
        verbose_name = 'Afectación'
        verbose_name_plural = 'Afectaciones'
