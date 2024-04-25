from django.db import models

from notes.models import Nota
from projects.models import Proyecto
from tempo_extend.models import Temporalidad
from ubication.models import Ubicacion


# CREATE TABLE ocs.cat_tipo_afectaciones_sociales (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoAfectacionesSociales(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Afectación Social'
        verbose_name_plural = 'Tipos Afectaciones Sociales'
        db_table = 'cat_tipo_afectaciones_sociales'


# CREATE TABLE ocs.afectaciones_sociales (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_as_id integer,  --ForeignKey
#     descripcion_as text,
#     temporalidad_id integer  --ForeignKey
# );

class AfectacionesSociales(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_as = models.ForeignKey(
        TipoAfectacionesSociales, on_delete=models.CASCADE)
    descripcion_as = models.TextField()
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.as_to_ubicaciones')

    def __str__(self):
        return self.tipo_as.nombre

    class Meta:
        verbose_name = 'Afectación Social'
        verbose_name_plural = 'Afectaciones Sociales'
        db_table = 'afectaciones_sociales'

# # --ubicaciones

# CREATE TABLE ocs.as_to_ubicaciones (
#     id integer NOT NULL,
#     afectacion_social_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );
