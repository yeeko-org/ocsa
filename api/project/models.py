from django.db import models
# from space_time.models import Location
from work_flux.models import StatusControl, CommentsMixin
from profile_auth.models import User
from utils.mix_models import CatalogGroup, CatalogType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from space_time.models import Location


class ExtractivismType(CatalogGroup):
    short_name = models.CharField(max_length=100, blank=True, null=True)
    ai_name = models.CharField(
        max_length=255, blank=True, null=True,
        help_text='Nombre para IA, si es diferente al nombre')
    icon_image = models.ImageField(
        upload_to='icons/', blank=True, null=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Tipo de Extractivismo'
        verbose_name_plural = 'Tipos de Extractivismo'


class MegaprojectType(CatalogType):
    extractivism_types = models.ManyToManyField(
        ExtractivismType, blank=True, related_name='megaproject_types')
    has_many_dct = models.BooleanField(
        default=False, verbose_name='Difiere en Tipo de Extractivismo')

    class Meta:
        ordering = ['order']
        verbose_name = 'Tipo de Megaproyecto'
        verbose_name_plural = 'Tipos de Megaproyecto'


class StatusProject(CatalogType):

    class Meta:
        ordering = ["order", "name"]
        verbose_name = 'Estatus del Proyecto'
        verbose_name_plural = 'Estatus de proyectos'


class Conflict(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Conflicto Socioambiental'
        verbose_name_plural = 'Conflictos Socioambientales'


class Project(CommentsMixin):
    proyecto_id_ref = models.IntegerField(blank=True, null=True)
    legacy_id_mp = models.IntegerField(blank=True, null=True)
    name = models.CharField(
        max_length=255, verbose_name='Nombre común', blank=True, null=True)
    alternative_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent_project = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        verbose_name='Proyecto en el que se agrupa',
        blank=True, null=True, related_name='children_projects')
    others_parents = models.ManyToManyField(
        'self', blank=True,
        verbose_name='Otros proyectos en los que se agrupa',
        related_name='others_children_projects')
    conflict = models.ForeignKey(
        Conflict, on_delete=models.CASCADE, blank=True, null=True,
        related_name='projects')
    megaproject_type = models.ForeignKey(
        MegaprojectType, on_delete=models.CASCADE, blank=True, null=True,
        related_name='projects')
    is_grouper = models.BooleanField(default=False)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True,
        related_name='projects')
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True,
        related_name='project_register')
    status_location = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True,
        related_name='project_location')
    editors = models.ManyToManyField(
        User, blank=True, related_name='projects')

    incongruent = models.BooleanField(default=False)
    prev_status_loc = models.CharField(max_length=60, blank=True, null=True)

    files: models.QuerySet["ProjectFile"]
    status_location_id: str | None
    locations: models.QuerySet["Location"]

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

    @property
    def first_location(self):
        if hasattr(self, 'ordered_locations'):
            return self.ordered_locations[0] if self.ordered_locations else None
        return self.locations.select_related('state', 'municipality', 'locality').order_by(
            '-status_location__priority').first()

    def __str__(self):
        return self.name or "Proyecto sin nombre"

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'


def upload_to_project_file(instance, filename):
    return f'project_file/{instance.project.pk}/{filename}'


class ProjectFile(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_to_project_file, max_length=255)
    old_ref = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name if self.file else 'Archivo sin nombre'

    class Meta:
        verbose_name = 'Archivo de proyecto'
        verbose_name_plural = 'Archivos de proyecto'


# class ProjectLocation(models.Model):
#     project = models.ForeignKey(
#         Project, on_delete=models.CASCADE, related_name='locations')
#     location = models.ForeignKey(
#         Location, on_delete=models.CASCADE, related_name='projects')
#     # location = models.OneToOneField(
#     #     Location, on_delete=models.CASCADE, related_name='project_location')
#     status_location = models.ForeignKey(
#         StatusControl, on_delete=models.CASCADE, blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.project} - {self.location}"
#
#     class Meta:
#         verbose_name = 'Ubicación de proyecto'
#         verbose_name_plural = 'Ubicaciones de proyectos'


# def identify_projects_with_many_project_locations():
#     from project.models import ProjectLocation
#     from django.db.models import Count
#
#     projects = ProjectLocation.objects.values('project').annotate(
#         count=Count('project')).filter(count__gt=1)
#     print(projects)
