from django.db import models


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
