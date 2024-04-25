from django.db import models

# CREATE TABLE ocs.cat_sector_social (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class SectorSocial(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Sector Social'
        verbose_name_plural = 'Sectores Sociales'
        db_table = 'cat_sector_social'

# CREATE TABLE ocs.cat_condicion_mujer_victima (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class CondicionMujerVictima(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Condición Mujer Víctima'
        verbose_name_plural = 'Condiciones Mujer Víctima'
        db_table = 'cat_condicion_mujer_victima'
