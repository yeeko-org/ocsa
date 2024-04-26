from django.db import models


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
