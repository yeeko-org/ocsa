from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        db_table = 'countries'


class StatusProject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Status Project'
        verbose_name_plural = 'Status Projects'


# ======================== VERSIÓN 1: ========================================

# CREATE TABLE ocs.ubicaciones (
#     id integer NOT NULL,
#     tipo_ubicacion ocs.tipo_ubicacion_e DEFAULT 'punto'::ocs.tipo_ubicacion_e,
#     estado text,
#     municipio text,
#     localidad text,
#     especificaciones text,
#     sitio text,
#     latitud double precision,
#     longitud double precision,
#     geom text
# );


class Ubicacion(models.Model):
    tipo_ubicacion = models.CharField(max_length=100, default='punto')
    estado = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    especificaciones = models.TextField()
    sitio = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()
    geom = models.TextField()

    def __str__(self):
        return self.sitio

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        db_table = 'ubicaciones'

# CREATE TABLE ocs.cat_temporalidad (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class CatTemporalidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Temporalidad'
        verbose_name_plural = 'Temporalidades'
        db_table = 'cat_temporalidad'


# CREATE TABLE ocs.temporalidad (
#     id integer NOT NULL,
#     fecha date,
#     intervalo interval,
#     day_undefined boolean DEFAULT false,
#     month_undefined boolean DEFAULT false,
#     cat_temporalidad_id integer  --ForeignKey
# );

class Temporalidad(models.Model):
    fecha = models.DateField()
    intervalo = models.DurationField()
    day_undefined = models.BooleanField(default=False)
    month_undefined = models.BooleanField(default=False)
    cat_temporalidad = models.ForeignKey(
        CatTemporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.fecha

    class Meta:
        verbose_name = 'Temporalidad'
        verbose_name_plural = 'Temporalidades'
        db_table = 'temporalidad'
