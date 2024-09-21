from django.db import models
from django.db.models import JSONField
from space_time.models import StatusProject
from space_time.models import Location
from work_flux.models import StatusControl


class DeploymentCapitalType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    icon_image = models.ImageField(
        upload_to='icons/', blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'


# El registro de esta tabla es desde "cat_tipo_megaproyecto",
# para el name (que viene de nombre)
# sin embargo, deployment_capital_types lo vamos a construir
# a partir de la tabla Proyecto, sin embargo, es posible que un
# mismo tipo de megaproyecto tenga diferentes tipos de despliegue de
# capital, en esos casos, debe marcarse el campo has_many_dct como True
class MegaprojectType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deployment_capital_types = models.ManyToManyField(
        DeploymentCapitalType, blank=True)
    has_many_dct = models.BooleanField(
        default=False, verbose_name='Difiere en Tipo de Despliegue Capital')
    # common_affection_types = models.ManyToManyField(
    #     'impact.AffectionType', blank=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Megaproyecto'
        verbose_name_plural = 'Tipos de Megaproyecto'


# Este no tiene mayor complicación y se genera con el campo Proyecto.escala
class Scale(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Escala de los proyectos'
        verbose_name_plural = 'Escalas de los proyectos'


# Viene de la tabla CSA
class Conflict(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Conflicto Socioambiental'
        verbose_name_plural = 'Conflictos Socioambientales'


# CASO 1, simple
# Proyecto A --> Proyecto B
# Proyecto B
# Proyecto C (CLUSTER CREADO desde Proyecto B)
# Proyecto A.parent_project = Proyecto C
# Proyecto C.parent_project = Proyecto C

# CASO 2, doble relación
# Proyecto A --> Proyecto B
# Proyecto B --> Proyecto A
# Proyecto C (CLUSTER CREADO desde Proyecto B)
# Proyecto A.parent_project = Proyecto C
# Proyecto C.parent_project = Proyecto C

class Project(models.Model):
    proyecto_id_ref = models.IntegerField(blank=True, null=True)
    legacy_id_mp = models.IntegerField(blank=True, null=True)

    # Viene de Proyecto.nombre
    official_name = models.CharField(
        max_length=255, verbose_name='Nombre oficial', blank=True, null=True)
    common_name = models.CharField(
        max_length=255, verbose_name='Nombre común', blank=True, null=True)
    alternative_name = models.TextField(blank=True, null=True)
    # Viene del campo Proyecto.especificaciones, excepto si su valor es "SD",
    # en ese caso ignorarlo.
    description = models.TextField(blank=True, null=True)
    parent_project = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        verbose_name='Proyecto en el que se agrupa',
        blank=True, null=True)
    others_parents = models.ManyToManyField(
        'self', blank=True, verbose_name='Otros proyectos en los que se agrupa')
    # Campo Proyecto.csa
    conflict = models.ForeignKey(
        Conflict, on_delete=models.CASCADE, blank=True, null=True)
    megaproject_type = models.ForeignKey(
        MegaprojectType, on_delete=models.CASCADE, blank=True, null=True)
    # extensión tipo ??? c150
    scale = models.ForeignKey(
        Scale, on_delete=models.CASCADE, blank=True, null=True)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
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
