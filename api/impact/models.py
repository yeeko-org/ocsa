from django.db import models

from source.models import Nota
from project.models import Proyecto
from space_time.models import Ubicacion, Temporalidad
from utils.obj_str import nombre_or_pk


# --------------------- Afectaciones ecológicas --------------------------------

# CREATE TABLE ocs.cat_tipo_afectaciones_ecologicas (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoAfectacionesEcologicas(models.Model):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_ae = models.ForeignKey(
        TipoAfectacionesEcologicas, on_delete=models.CASCADE, blank=True, null=True)
    descripcion_ae = models.TextField(blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.ae_to_ubicaciones', blank=True)

    def __str__(self):
        return nombre_or_pk(self.tipo_ae, self.pk)

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


# CREATE TABLE ocs.cat_tipo_afectaciones_sociales (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class TipoAfectacionesSociales(models.Model):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_as = models.ForeignKey(
        TipoAfectacionesSociales, on_delete=models.CASCADE, blank=True, null=True)
    descripcion_as = models.TextField(blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.as_to_ubicaciones', blank=True)

    def __str__(self):
        return nombre_or_pk(self.tipo_as, self.pk)

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


# CREATE TABLE ocs.otros (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_propiedad text,
#     fortalecimiento_tejido_social text,
#     descripcion text
# );


class Otros(models.Model):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_propiedad = models.TextField(blank=True, null=True)
    fortalecimiento_tejido_social = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tipo_propiedad or str(self.pk)

    class Meta:
        verbose_name = 'Otro'
        verbose_name_plural = 'Otros'
        db_table = 'otros'
