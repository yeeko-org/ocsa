from django.db import models
from django.db.models import JSONField
from space_time.models import StatusProject
from space_time.models import Location
from work_flux.models import StatusControl


class ExtractivismType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    icon_image = models.ImageField(
        upload_to='icons/', blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'


class MegaprojectType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    extractivism_types = models.ManyToManyField(
        ExtractivismType, blank=True)
    has_many_dct = models.BooleanField(
        default=False, verbose_name='Difiere en Tipo de Despliegue Capital')
    # common_affection_types = models.ManyToManyField(
    #     'impact.AffectionType', blank=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Tipo de Megaproyecto'
        verbose_name_plural = 'Tipos de Megaproyecto'


class Scale(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Escala de los proyectos'
        verbose_name_plural = 'Escalas de los proyectos'


class Conflict(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Conflicto Socioambiental'
        verbose_name_plural = 'Conflictos Socioambientales'


class Project(models.Model):
    proyecto_id_ref = models.IntegerField(blank=True, null=True)
    legacy_id_mp = models.IntegerField(blank=True, null=True)
    official_name = models.CharField(
        max_length=255, verbose_name='Nombre oficial', blank=True, null=True)
    common_name = models.CharField(
        max_length=255, verbose_name='Nombre común', blank=True, null=True)
    alternative_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent_project = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        verbose_name='Proyecto en el que se agrupa',
        blank=True, null=True)
    others_parents = models.ManyToManyField(
        'self', blank=True, verbose_name='Otros proyectos en los que se agrupa')
    conflict = models.ForeignKey(
        Conflict, on_delete=models.CASCADE, blank=True, null=True)
    megaproject_type = models.ForeignKey(
        MegaprojectType, on_delete=models.CASCADE, blank=True, null=True,
        related_name='projects')
    scale = models.ForeignKey(
        Scale, on_delete=models.CASCADE, blank=True, null=True)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True,
        related_name='project_register')
    status_location = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True,
        related_name='project_location')
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.official_name or self.common_name or "Proyecto sin nombre"

    def get_last_status_project(self, save=False):
        from source.models import StatusHistory
        last_status_history = StatusHistory.objects\
            .filter(mention__project=self).order_by('date').last()
        if last_status_history:
            self.status_project = last_status_history.status_project
            if save:
                self.save()
            return self.status_project
        return None

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'


class ProjectLocation(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='locations')
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='projects')
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.project} - {self.location}"

    class Meta:
        verbose_name = 'Ubicación de proyecto'
        verbose_name_plural = 'Ubicaciones de proyectos'
