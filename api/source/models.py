from django.db import models

from project.models import Proyecto, EstatusProyecto, Project
from space_time.models import Temporalidad, StatusProject
from work_flux.models import StatusControl


class Source(models.Model):
    name = models.CharField(max_length=100)
    is_news = models.BooleanField(blank=True, null=True)
    main_url = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'


class Note(models.Model):
    title = models.CharField(max_length=100)
    old_id = models.IntegerField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
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


# ============================================================================
# ======================== VERSIÓN 1: ========================================
# CREATE TABLE ocs.notas (
#     id integer NOT NULL,
#     id_nota integer,
#     titulo text,
#     autor text,
#     nombre_medio text,
#     pagina_medio text,
#     vinculo text,
#     fecha date,
#     fecha_captura date
# );

class Nota(models.Model):
    id_nota = models.IntegerField(blank=True, null=True)
    titulo = models.TextField(blank=True, null=True)
    autor = models.TextField(blank=True, null=True)
    nombre_medio = models.TextField(blank=True, null=True)
    pagina_medio = models.TextField(blank=True, null=True)
    vinculo = models.TextField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    fecha_captura = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.titulo or str(self.pk)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        db_table = 'notas'


# CREATE TABLE ocs.registro_notas (
#     id integer NOT NULL,
#     owner text,
#     datum jsonb,
#     status ocs.draft_status DEFAULT 'inprogress'::ocs.draft_status,
#     last_edit timestamp with time zone DEFAULT CURRENT_TIMESTAMP
# );


# ALTER TABLE ocs.registro_notas ENABLE ROW LEVEL SECURITY;

class RegistroNotas(models.Model):
    owner = models.TextField(blank=True, null=True)
    datum = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=100, default='inprogress', blank=True, null=True)
    last_edit = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.owner or str(self.pk)

    class Meta:
        verbose_name = 'Registro Nota'
        verbose_name_plural = 'Registros Notas'
        db_table = 'registro_notas'


# CREATE TABLE ocs.estatus_proyectos (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     estatus_id integer,  --ForeignKey
#     temporalidad_id integer  --ForeignKey
# );

# LUCIAN, hay que pasar esto a "source"
class EstatusProyectos(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    estatus = models.ForeignKey(EstatusProyecto, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.nota

    class Meta:
        verbose_name = 'Estatus Proyecto'
        verbose_name_plural = 'Estatus Proyectos'
        db_table = 'estatus_proyectos'

