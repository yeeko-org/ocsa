from django.db import models

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
