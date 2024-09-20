from django.db import models
from django.db.models import JSONField
from source.models import Mention


class ImpactType(models.Model):
    name = models.CharField(max_length=255)
    has_subtype = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    # TODO Nuevas migraciones, incorporarlas en el frontend
    order = models.SmallIntegerField(default=0)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    is_social = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Impacto'
        verbose_name_plural = 'Tipos de Impactos'


class ImpactSubtype(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    impact_type = models.ForeignKey(ImpactType, on_delete=models.CASCADE)
    help_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subtipo de Impacto'
        verbose_name_plural = 'Subtipos de Impactos'


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
        verbose_name = 'Impacto'
        verbose_name_plural = 'Impactos'
