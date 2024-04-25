from django.db import models

from notes.models import Nota
from projects.models import Proyecto
from tempo_extend.models import Temporalidad
from ubication.models import Ubicacion


# --------------------- Afectaciones ecológicas --------------------------------

# CREATE TABLE ocs.cat_tipo_afectaciones_ecologicas (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoAfectacionesEcologicas(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Tipo Afectación Ecológica'
        verbose_name_plural = 'Tipos Afectaciones Ecológicas'
        db_table = 'cat_tipo_afectaciones_ecologicas'

# CREATE TABLE ocs.afectaciones_ecologicas (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_ae_id integer,  --ForeignKey
#     descripcion_ae text,
#     temporalidad_id integer  --ForeignKey
# );


class AfectacionesEcologicas(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_ae = models.ForeignKey(
        TipoAfectacionesEcologicas, on_delete=models.CASCADE)
    descripcion_ae = models.TextField()
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.ae_to_ubicaciones')

    def __str__(self):
        return self.tipo_ae.nombre

    class Meta:
        verbose_name = 'Afectación Ecológica'
        verbose_name_plural = 'Afectaciones Ecológicas'
        db_table = 'afectaciones_ecologicas'


# --ubicaciones

# CREATE TABLE ocs.ae_to_ubicaciones (
#     id integer NOT NULL,
#     afectacion_ecologica_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );
