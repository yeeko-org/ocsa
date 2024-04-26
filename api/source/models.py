from django.db import models


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
