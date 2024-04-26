from django.db import models

from source.models import Nota
from space_time.models import Ubicacion, Temporalidad
from utils.obj_str import nombre_or_pk


# --------------------- Conflictos SocioAmbientales ---------------------------


# CREATE TABLE ocs.csa (
#     id integer NOT NULL,
#     nombre text
# );


class CSA(models.Model):
    nombre = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        verbose_name = 'CSA'
        verbose_name_plural = 'CSAs'
        db_table = 'csa'

# ------------------------------ Proyectos --------------------------------


# -- Clasificaciones de proyecto


# CREATE TABLE ocs.cat_tipo_despliegue_capital (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text,
#     icono text,
#     color text
# );
class TipoDespliegueCapital(models.Model):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'
        db_table = 'cat_tipo_despliegue_capital'


# CREATE TABLE ocs.cat_tipo_megaproyecto (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoMegaproyecto(models.Model):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        verbose_name = 'Tipo Megaproyecto'
        verbose_name_plural = 'Tipos Megaproyecto'
        db_table = 'cat_tipo_megaproyecto'

# CREATE TABLE ocs.cat_estatus_proyecto (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class EstatusProyecto(models.Model):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        verbose_name = 'Estatus Proyecto'
        verbose_name_plural = 'Estatus Proyectos'
        db_table = 'cat_estatus_proyecto'


# CREATE TABLE ocs.proyectos (
#     id integer NOT NULL,
#     id_mp integer,
#     nombre text,
#     escala text,
#     tipo_despliegue_capital_id integer,  --ForeignKey
#     tipo_megaproyecto_id integer,  --ForeignKey
#     especificaciones text,
#     csa_id integer,  --ForeignKey
#     proyecto_vinculado_id integer,  --ForeignKey
#     old_ubis bigint
# );
class Proyecto(models.Model):
    id_mp = models.IntegerField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    escala = models.TextField(blank=True, null=True)
    tipo_despliegue_capital = models.ForeignKey(
        TipoDespliegueCapital, on_delete=models.CASCADE, blank=True, null=True)
    tipo_megaproyecto = models.ForeignKey(
        TipoMegaproyecto, on_delete=models.CASCADE, blank=True, null=True)
    especificaciones = models.TextField(blank=True, null=True)
    csa = models.ForeignKey(
        CSA, on_delete=models.CASCADE, blank=True, null=True)
    proyecto_vinculado = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True)
    old_ubis = models.BigIntegerField(blank=True, null=True)
    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.proyectos_to_ubicaciones', blank=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        db_table = 'proyectos'


# CREATE TABLE ocs.estatus_proyectos (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     estatus_id integer,  --ForeignKey
#     temporalidad_id integer  --ForeignKey
# );
class EstatusProyectos(models.Model):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    estatus = models.ForeignKey(
        EstatusProyecto, on_delete=models.CASCADE, blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.nota, self.pk, 'titulo')

    class Meta:
        verbose_name = 'Estatus Proyecto'
        verbose_name_plural = 'Estatus Proyectos'
        db_table = 'estatus_proyectos'

# --ubicaciones

# CREATE TABLE ocs.proyectos_to_ubicaciones (
#     id bigint NOT NULL,
#     proyecto_id bigint,
#     ubicacion_id bigint
# );

# class ProyectosToUbicaciones(models.Model):
#     proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, blank=True, null=True)
#     ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, blank=True, null=True)

#     def __str__(self):
#         return self.proyecto.nombre

#     class Meta:
#         verbose_name = 'Proyecto a Ubicación'
#         verbose_name_plural = 'Proyectos a Ubicaciones'
#         db_table = 'proyectos_to_ubicaciones'
