from django.db import models
from django.db.models import JSONField


class Country(models.Model):
    name = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class StatusProject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Status Project'
        verbose_name_plural = 'Status Projects'


def default_alternative_names():
    return []


# Para estados vas a utilizar la lista de initial_data y vas a tomar las
# alternative_names del campo other_names, separados por comas.
class State(models.Model):
    inegi_code = models.CharField(max_length=2, verbose_name="Clave INEGI")
    name = models.CharField(max_length=50, verbose_name="Nombre")
    short_name = models.CharField(
        max_length=20, verbose_name="Nombre Corto",
        blank=True, null=True)
    code_name = models.CharField(
        max_length=6, verbose_name="Nombre Clave",
        blank=True, null=True)
    alternative_names = JSONField(
        default=default_alternative_names,
        verbose_name="Lista nombres alternativos",
        help_text="Ocupar para OCAMIS",
        )

    def __str__(self):
        return self.short_name or self.code_name or self.name

    class Meta:
        ordering = ["inegi_code"]
        verbose_name = "Entidad Federativa"
        verbose_name_plural = "Entidades Federativas"


# Para municipios vamos a tomar el archivo municipios.csv y vas a tomar las
# siguientes columnas:
# CVE_ENT --> Municipality.state.inegi_code
# CVE_MUN --> Municipality.inegi_code
# NOM_MUN --> Municipality.name
# POB_TOTAL --> Municipality.population
# complete_code lo puedes generar con la concatenación de Cve_Ent y Cve_Mun,
# en medio de ellos un guión.

class Municipality(models.Model):

    inegi_code = models.CharField(max_length=6, verbose_name="Clave INEGI")
    complete_code = models.CharField(
        max_length=8, verbose_name="Clave INEGI Completa")
    name = models.CharField(max_length=120, verbose_name="Nombre")
    state = models.ForeignKey(
        State, verbose_name=State,
        null=True, on_delete=models.CASCADE,
        related_name="municipalities")
    population = models.IntegerField(
        blank=True, null=True, verbose_name="Población")

    def __str__(self):
        return "%s - %s" % (self.name, self.state)

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ["inegi_code"]


# Para localidad, hay un archivo de .txt y un archivo de .csv, con el que sea
# más sencillo, con ese, vas a tomar las siguientes columnas:
# CVE_ENT --> Locality.municipality.state.inegi_code
# CVE_MUN --> Locality.municipality.inegi_code
# CVE_LOC --> Locality.inegi_code
# NOM_LOC --> Locality.name
# POB_TOTAL --> Locality.population
# LAT_DECIMAL --> Locality.latitude
# LON_DECIMAL --> Locality.longitude
# ALTITUD --> Locality.altitude

class Locality(models.Model):
    inegi_code = models.CharField(max_length=6, verbose_name="Clave INEGI")
    complete_code = models.CharField(
        max_length=10, verbose_name="Clave INEGI Completa")
    name = models.CharField(max_length=120, verbose_name="Nombre")
    municipality = models.ForeignKey(
        Municipality, verbose_name=Municipality,
        null=True, on_delete=models.CASCADE,
        related_name="localities")
    population = models.IntegerField(
        blank=True, null=True, verbose_name="Población")
    is_rural = models.BooleanField(default=False, verbose_name="Es rural")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    altitude = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.municipality)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"


class Location(models.Model):
    state = models.ForeignKey(
        State, on_delete=models.CASCADE,
        related_name="locations")
    municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE,
        related_name="locations")
    locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE,
        related_name="locations")
    details = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    # LUCIAN: Esto debe ser JSON, Point ¿o de qué tipo?, ¿cómo lo nombramos?
    # geom = models.PointField(blank=True, null=True)
