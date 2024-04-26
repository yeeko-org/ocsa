from django.db import models
from django.db.models import JSONField
from source.models import Nota, Note
from space_time.models import Ubicacion, Temporalidad, StatusProject


class DeploymentCapitalType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'


class MegaprojectType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    deployment_capital_types = models.ManyToManyField(
        DeploymentCapitalType, blank=True)
    # common_affection_types = models.ManyToManyField(
    #     'impact.AffectionType', blank=True)
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    interests = JSONField(
        blank=True, null=True, verbose_name='Intereses (final)')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Megaproyecto'
        verbose_name_plural = 'Tipos de Megaproyecto'


class Scale(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Escala de los proyectos'
        verbose_name_plural = 'Escalas de los proyectos'


class Conflict(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Conflict'
        verbose_name_plural = 'Conflicts'
        db_table = 'conflicts'


class Project(models.Model):
    official_name = models.CharField(
        max_length=255, verbose_name='Nombre oficial', blank=True, null=True)
    common_name = models.CharField(
        max_length=255, verbose_name='Nombre común', blank=True, null=True)
    alternative_name = models.TextField()
    parent_project = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        verbose_name='Proyecto en el que se agrupa')
    conflict = models.ForeignKey(
        Conflict, on_delete=models.CASCADE, blank=True, null=True)
    megaproject_type = models.ForeignKey(
        MegaprojectType, on_delete=models.CASCADE, blank=True, null=True)
    # extensión tipo ??? c150
    scale = models.ForeignKey(
        Scale, on_delete=models.CASCADE, blank=True, null=True)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.official_name or self.common_name or "Proyecto sin nombre"

    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        db_table = 'projects'


# LUCIAN: Temporalmente aquí, pero debería ir en la app source:
class Mention(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    # RICK: Aún no sé si esto debería ser not null
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
    filled = models.BooleanField(default=False)
    date_filled = models.DateField(blank=True, null=True)
    # editor = models.ForeignKey(
    #     'users.User', on_delete=models.CASCADE, blank=True, null=True)
    # reviewer = models.ForeignKey(
    #     'users.User', on_delete=models.CASCADE, blank=True, null=True)
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)




# ======================== VERSIÓN 1: ========================================
# --------------------- Conflictos SocioAmbientales ---------------------------

# CREATE TABLE ocs.csa (
#     id integer NOT NULL,
#     nombre text
# );


class CSA(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

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
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.CharField(max_length=100)
    color = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

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
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

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
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

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
    id_mp = models.IntegerField()
    nombre = models.CharField(max_length=100)
    escala = models.CharField(max_length=100)
    tipo_despliegue_capital = models.ForeignKey(
        TipoDespliegueCapital, on_delete=models.CASCADE)
    tipo_megaproyecto = models.ForeignKey(
        TipoMegaproyecto, on_delete=models.CASCADE)
    especificaciones = models.TextField()
    csa = models.ForeignKey(CSA, on_delete=models.CASCADE)
    proyecto_vinculado = models.ForeignKey('self', on_delete=models.CASCADE)
    old_ubis = models.BigIntegerField()
    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.proyectos_to_ubicaciones')

    def __str__(self):
        return self.nombre

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
# LUCIAN, hay que pasar esto a "source"
class EstatusProyectos(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    estatus = models.ForeignKey(EstatusProyecto, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.nota.titulo

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
#     proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
#     ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.proyecto.nombre

#     class Meta:
#         verbose_name = 'Proyecto a Ubicación'
#         verbose_name_plural = 'Proyectos a Ubicaciones'
#         db_table = 'proyectos_to_ubicaciones'
