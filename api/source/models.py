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
    id_nota = models.IntegerField()
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    nombre_medio = models.CharField(max_length=100)
    pagina_medio = models.CharField(max_length=100)
    vinculo = models.CharField(max_length=100)
    fecha = models.DateField()
    fecha_captura = models.DateField()

    def __str__(self):
        return self.titulo

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
    owner = models.CharField(max_length=100)
    datum = models.JSONField()
    status = models.CharField(max_length=100, default='inprogress')
    last_edit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner

    class Meta:
        verbose_name = 'Registro Nota'
        verbose_name_plural = 'Registros Notas'
        db_table = 'registro_notas'
