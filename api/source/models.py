from django.db import models

from project.models import Project
from space_time.models import StatusProject
from work_flux.models import StatusControl


class Source(models.Model):
    name = models.CharField(max_length=100)
    is_news = models.BooleanField(blank=True, null=True)
    main_url = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.main_url or 'unknown'} - {self.is_news or 'unknown'}"

    class Meta:
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'


class Note(models.Model):
    title = models.CharField(max_length=255)
    old_id = models.IntegerField(blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    # En teoría, tendría que haber 2 fuentes, La Jornada y Reforma,
    # pero sí hay más, pues hay que registrarlas, pero con is_news=False
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    link = models.CharField(max_length=255, blank=True, null=True)
    screenshot = models.ImageField(
        upload_to='screenshots/', blank=True, null=True)
    date = models.DateField()
    capture_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


# El primer lugar de donde viene este registro es de EstatusProyectos,
# Antes de comenzar, deberás migrar todos los registros de EstatusProyecto que
# ahora se llama StatusProject
# EstatusProyectos tiene la relación entre Note y Project. Por ahora vamos a
# ignorar la tabla "temporalidad" pero sí tomaremos en cuenta Proyecto."estatus"
class Mention(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    # RICK: Aún no sé si esto debería ser not null
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
    filled = models.BooleanField(default=False)
    date_filled = models.DateField(blank=True, null=True)
    # editor = models.ForeignKey(
    #     'users.User', on_delete=models.CASCADE, blank=True, null=True)
    # reviewer = models.ForeignKey(
    #     'users.User', on_delete=models.CASCADE, blank=True, null=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.note

    class Meta:
        verbose_name = 'Mención de proyecto en nota'
        verbose_name_plural = 'Menciones de proyectos en notas'
