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
