from django.db import models
from django.db.models import JSONField
from space_time.models import StatusProject


class DeploymentCapitalType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'


class MegaprojectType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    deployment_capital_types = models.ManyToManyField(
        DeploymentCapitalType, blank=True)
    # common_affection_types = models.ManyToManyField(
    #     'impact.AffectionType', blank=True)
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    interests = JSONField(
        blank=True, null=True, verbose_name='Intereses (final)')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Megaproyecto'
        verbose_name_plural = 'Tipos de Megaproyecto'


class Scale(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Escala de los proyectos'
        verbose_name_plural = 'Escalas de los proyectos'


class Conflict(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Conflict'
        verbose_name_plural = 'Conflicts'
        db_table = 'conflicts'


class Project(models.Model):
    official_name = models.CharField(
        max_length=255, verbose_name='Nombre oficial', blank=True, null=True)
    common_name = models.CharField(
        max_length=255, verbose_name='Nombre común', blank=True, null=True)
    alternative_name = models.TextField()
    parent_project = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        verbose_name='Proyecto en el que se agrupa')
    conflict = models.ForeignKey(
        Conflict, on_delete=models.CASCADE, blank=True, null=True)
    megaproject_type = models.ForeignKey(
        MegaprojectType, on_delete=models.CASCADE, blank=True, null=True)
    # extensión tipo ??? c150
    scale = models.ForeignKey(
        Scale, on_delete=models.CASCADE, blank=True, null=True)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.official_name or self.common_name or "Proyecto sin nombre"

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        db_table = 'projects'


