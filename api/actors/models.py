from django.db import models

from notes.models import Nota
from projects.models import Proyecto
from tempo_extend.models import Temporalidad
from ubication.models import Ubicacion


# --------------------- Capitalistas (actores) --------------------------------


# CREATE TABLE ocs.capital (
#     id integer NOT NULL,
#     proyecto_id integer NOT NULL,  --ForeignKey
#     nota_id integer,  --ForeignKey
#     nombre text,
#     matriz text,
#     filial text,
#     directores text,
#     inversionistas text,
#     nacionalidad text,
#     is_capital_publico boolean,
#     is_cotiza_bolsa boolean,
#     interes text,
#     is_activo boolean
# );

class Capital(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    matriz = models.TextField()
    filial = models.TextField()
    directores = models.TextField()
    inversionistas = models.TextField()
    nacionalidad = models.CharField(max_length=100)
    is_capital_publico = models.BooleanField()
    is_cotiza_bolsa = models.BooleanField()
    interes = models.TextField()
    is_activo = models.BooleanField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Capital'
        verbose_name_plural = 'Capitales'
        db_table = 'capital'


# ------------------ Instituciones del estado (actores) ------------------------


# CREATE TABLE ocs.estado (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     instituciones_a_favor_proyecto text,
#     instituciones_mediadoras text,
#     instituciones_atienden_reclamos text,
#     temporalidad_id integer  --ForeignKey
# );

class Estado(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    instituciones_a_favor_proyecto = models.TextField()
    instituciones_mediadoras = models.TextField()
    instituciones_atienden_reclamos = models.TextField()
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.proyecto.nombre

    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        db_table = 'estado'


# --------------------- Opositores (actores) --------------------------------

# -- cats

# CREATE TABLE ocs.cat_forma_organizacion (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class FormaOrganizacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Forma Organización'
        verbose_name_plural = 'Formas Organización'
        db_table = 'cat_forma_organizacion'


# CREATE TABLE ocs.cat_mujer (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class Mujer(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Mujer'
        verbose_name_plural = 'Mujeres'
        db_table = 'cat_mujer'


# -- opositores

# CREATE TABLE ocs.opositores (
#     id integer NOT NULL,
#     nombre text,
#     forma_organizacion_id integer,  --ForeignKey
#     is_indigena boolean,
#     pueblo_indigena text,
#     is_campesino_or_comunero_or_ejidatario boolean,
#     mujer_id integer,  --ForeignKey
#     is_trabajador_empresa boolean,
#     otros_opositores text,
#     is_habitante_zona boolean
# );

class Opositor(models.Model):
    nombre = models.CharField(max_length=100)
    forma_organizacion = models.ForeignKey(
        FormaOrganizacion, on_delete=models.CASCADE)
    is_indigena = models.BooleanField()
    pueblo_indigena = models.CharField(max_length=100)
    is_campesino_or_comunero_or_ejidatario = models.BooleanField()
    mujer = models.ForeignKey(Mujer, on_delete=models.CASCADE)
    is_trabajador_empresa = models.BooleanField()
    otros_opositores = models.TextField()
    is_habitante_zona = models.BooleanField()

    proyectos = models.ManyToManyField(
        Proyecto, db_table='ocs.opositores_to_proyecto')
    notas = models.ManyToManyField(Nota, db_table='ocs.opositores_to_notas')
    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.opositores_to_ubicaciones')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Opositor'
        verbose_name_plural = 'Opositores'
        db_table = 'opositores'


# -- relacionales

# CREATE TABLE ocs.opositores_to_proyecto (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     proyecto_id integer  --ForeignKey
# );

# CREATE TABLE ocs.opositores_to_notas (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     nota_id integer  --ForeignKey
# );


# --ubicaciones

# CREATE TABLE ocs.opositores_to_ubicaciones (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

# -- Intereses

# CREATE TABLE ocs.intereses_opositores (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     opositor_id integer,  --ForeignKey
#     interes text
# );

class InteresesOpositores(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    opositor = models.ForeignKey(Opositor, on_delete=models.CASCADE)
    interes = models.TextField()

    def __str__(self):
        return self.opositor.nombre

    class Meta:
        verbose_name = 'Interés Opositor'
        verbose_name_plural = 'Intereses Opositores'
        db_table = 'intereses_opositores'


# --------------------- Poblaciones (actores) --------------------------------

# -- Cats

# CREATE TABLE ocs.cat_poblacion_afectada (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class PoblacionAfectada(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Población Afectada'
        verbose_name_plural = 'Poblaciones Afectadas'
        db_table = 'cat_poblacion_afectada'


# CREATE TABLE ocs.cat_subpoblacion_afectada (
#     id integer NOT NULL,
#     id_subpoblacion_af integer,
#     nombre text,
#     descripcion text
# );

class SubpoblacionAfectada(models.Model):
    id_subpoblacion_af = models.IntegerField()
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Subpoblación Afectada'
        verbose_name_plural = 'Subpoblaciones Afectadas'
        db_table = 'cat_subpoblacion_afectada'

# -- Poblaciones

# CREATE TABLE ocs.poblaciones_afectadas (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     poblacion_afectada_id integer,  --ForeignKey
#     subpoblacion_afectada_id integer,  --ForeignKey
#     descripcion text,
#     interes text,
#     ubicacion_id integer  --ForeignKey
# );


class PoblacionesAfectadas(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    poblacion_afectada = models.ForeignKey(
        PoblacionAfectada, on_delete=models.CASCADE)
    subpoblacion_afectada = models.ForeignKey(
        SubpoblacionAfectada, on_delete=models.CASCADE)
    descripcion = models.TextField()
    interes = models.TextField()
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.poblacion_afectada.nombre

    class Meta:
        verbose_name = 'Población Afectada'
        verbose_name_plural = 'Poblaciones Afectadas'
        db_table = 'poblaciones_afectadas'


# -- intereses

# CREATE TABLE ocs.intereses_poblacion (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     poblacion_afectada_id integer,  --ForeignKey
#     interes text
# );

class InteresesPoblacion(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    poblacion_afectada = models.ForeignKey(
        PoblacionAfectada, on_delete=models.CASCADE)
    interes = models.TextField()

    def __str__(self):
        return self.poblacion_afectada.nombre

    class Meta:
        verbose_name = 'Interés Población'
        verbose_name_plural = 'Intereses Poblaciones'
        db_table = 'intereses_poblacion'
