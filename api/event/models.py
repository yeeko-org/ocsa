from django.db import models

from actors.models import Opositor
from source.models import Nota
from project.models import Proyecto
from space_time.models import Ubicacion, Temporalidad


# # --------------------- Violencias (eventos) --------------------------------


# CREATE TABLE ocs.cat_hechos_violencia (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class HechosViolencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Hecho Violencia'
        verbose_name_plural = 'Hechos Violencia'
        db_table = 'cat_hechos_violencia'


# CREATE TABLE ocs.cat_forma_hecho_violencia (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class FormaHechoViolencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Forma Hecho Violencia'
        verbose_name_plural = 'Formas Hecho Violencia'
        db_table = 'cat_forma_hecho_violencia'


# CREATE TABLE ocs.violencias (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     hecho_violencia_id integer,  --ForeignKey
#     forma_hecho_violencia_id integer,  --ForeignKey
#     temporalidad_id integer,  --ForeignKey
#     num_victimas text,
#     is_hombres boolean,
#     is_mujeres boolean,
#     condicion_mujeres_victimas integer,
#     sector_social_victima integer,
#     is_victima_dirigente boolean,
#     responsable_estatal_desc text,
#     responsable_no_estatal_desc text
# );

class Violencia(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    hecho_violencia = models.ForeignKey(
        HechosViolencia, on_delete=models.CASCADE)
    forma_hecho_violencia = models.ForeignKey(
        FormaHechoViolencia, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)
    num_victimas = models.TextField()
    is_hombres = models.BooleanField()
    is_mujeres = models.BooleanField()
    condicion_mujeres_victimas = models.ForeignKey(
        CondicionMujerVictima, on_delete=models.CASCADE)
    sector_social_victima = models.ForeignKey(
        SectorSocial, on_delete=models.CASCADE)
    is_victima_dirigente = models.BooleanField()
    responsable_estatal_desc = models.TextField()
    responsable_no_estatal_desc = models.TextField()

    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.violencias_to_ubicaciones')
    opositores = models.ManyToManyField(
        Opositor, db_table='ocs.violencias_to_opositores')

    def __str__(self):
        return self.hecho_violencia.nombre

    class Meta:
        verbose_name = 'Violencia'
        verbose_name_plural = 'Violencias'
        db_table = 'violencias'


# CREATE TABLE ocs.violencias_to_opositores (
#     id integer NOT NULL,
#     violencia_id integer,  --ForeignKey
#     opositor_id integer  --ForeignKey
# );


# # --ubicaciones

# CREATE TABLE ocs.violencias_to_ubicaciones (
#     id integer NOT NULL,
#     violencia_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

# # --------------------- Acciones colectivas (eventos) --------------------------------

# CREATE TABLE ocs.cat_forma_ac (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class FormaAC(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Forma Acción Colectiva'
        verbose_name_plural = 'Formas Acciones Colectivas'
        db_table = 'cat_forma_ac'


# CREATE TABLE ocs.cat_subforma_ac (
#     id integer NOT NULL,
#     id_forma_ac integer,
#     nombre text,
#     descripcion text
# );
class SubformaAC(models.Model):
    id_forma_ac = models.IntegerField()
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Subforma Acción Colectiva'
        verbose_name_plural = 'Subformas Acciones Colectivas'
        db_table = 'cat_subforma_ac'

# CREATE TABLE ocs.acciones_colectivas (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     forma_ac_id integer,  --ForeignKey
#     subforma_ac_id integer,  --ForeignKey
#     temporalidad_id integer  --ForeignKey
# );


class AccioneColectiva(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    forma_ac = models.ForeignKey(FormaAC, on_delete=models.CASCADE)
    subforma_ac = models.ForeignKey(SubformaAC, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.ac_to_ubicaciones')
    # LUCIAN: Esto no está ya en la tabla OpositoresToAC?, se tiene que declarar doble?
    opositores = models.ManyToManyField(Opositor, through='OpositoresToAC')

    def __str__(self):
        return self.forma_ac.nombre

    class Meta:
        verbose_name = 'Acción Colectiva'
        verbose_name_plural = 'Acciones Colectivas'
        db_table = 'acciones_colectivas'


# CREATE TABLE ocs.grupos_apoyo (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_grupo_apoyo text,
#     nombre text,
#     interes text
# );

class GruposApoyo(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_grupo_apoyo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    interes = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Grupo Apoyo'
        verbose_name_plural = 'Grupos Apoyo'
        db_table = 'grupos_apoyo'

# # -- relacional a opositor (y acción colectiva)

# CREATE TABLE ocs.opositores_to_ac (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     ac_id integer  --ForeignKey
# );


class OpositoresToAC(models.Model):
    opositor = models.ForeignKey(Opositor, on_delete=models.CASCADE)
    accione_colectiva = models.ForeignKey(
        AccioneColectiva, on_delete=models.CASCADE, db_column='ac_id')

    def __str__(self):
        return self.opositor.nombre

    class Meta:
        verbose_name = 'Opositor a Acción Colectiva'
        verbose_name_plural = 'Opositores a Acciones Colectivas'
        db_table = 'opositores_to_ac'

# # --ubicaciones

# CREATE TABLE ocs.ac_to_ubicaciones (
#     id integer NOT NULL,
#     accion_colectiva_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

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
