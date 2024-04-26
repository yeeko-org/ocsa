from django.db import models

from source.models import Nota, Note
from project.models import Proyecto, Project
from space_time.models import Ubicacion, Temporalidad, Country
from django.db.models import JSONField
from utils.obj_str import nombre_or_pk
# from work_flux.models import StatusRegister


init_participant_types = [
    ('Promotor', 'agree'),
    ('Financiador', 'agree'),
    ('Ejecutor del Proyecto', 'agree'),
    ('Beneficiario', 'agree'),
    ('Trabajadores', 'agree'),
    ('Represor', 'agree'),
    # los que tengan not null Estado.instituciones_medidoras
    ('Mediador', 'neutral'),
    # los que tengan not null Estado.instituciones_atienden_reclamos
    ('Atención a reclamos', 'neutral'),
    ('Acompañante', 'oppose'),  # Acompañamiento-apoyo (representante) con los afectados u opositores
    ('Afectado', 'oppose'),
    ('Opositor', 'oppose'),
    ('Habitante de la zona', 'oppose'),
    ('Otro', 'other'),
]

# estos se deben agregar con is_temporal = True
temporal_participant_types = [
    ('Capital', 'agree'),
    # solo los que tengan not null Estado.instituciones_a_favor_proyecto
    ('Estado', 'agree'),
    ('Estado', 'agree'),
    ('Opositor', 'oppose'),
    ('Población', 'oppose'),
    ('Grupo de Apoyo', 'agree'),
    ('Otro', 'other'),
]


class ParticipantType(models.Model):

    SIDE_CHOICES = (
        ('undefined', 'No definido'),
        ('agree', 'A favor'),
        ('oppose', 'En contra'),
        ('neutral', 'Neutral'),
        ('other', 'Otro'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_temporal = models.BooleanField(default=False)
    side = models.CharField(
        max_length=10, choices=SIDE_CHOICES, default='undefined')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Participación en Proyecto'
        verbose_name_plural = 'Tipos de Participación en Proyecto'


class Vulnerability(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Vulnerabilidad'
        verbose_name_plural = 'Vulnerabilidades'


# is_capital_publico => ESTADO

class SectorGroup(models.Model):
    name = models.CharField(max_length=255)
    is_collective = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Sectorial'
        verbose_name_plural = 'Grupos Sectoriales'


class Sector(models.Model):
    name = models.CharField(max_length=255)
    needs_name = models.BooleanField(default=False)
    sector_group = models.ForeignKey(
        SectorGroup, on_delete=models.CASCADE)
    sector_name = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='Nombre del sector (opcional)')
    common_participant_types = models.ManyToManyField(
        ParticipantType, blank=True)
    has_vulnerabilities = models.BooleanField(default=True)
    common_vulnerabilities = models.ManyToManyField(
        Vulnerability, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'


class CapitalType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Capital'
        verbose_name_plural = 'Tipos de Capital'


# Tablas origen: Capital, Estado, Opositores, Poblaciones, GruposApoyo
class Actor(models.Model):
    GEO_REACH_CHOICES = (
        ('local', 'Local'),
        ('regional', 'Regional'),
        ('national', 'Nacional'),
        ('international', 'Internacional'),
        ('global', 'Global'),
    )

    SEX_CHOICES = (
        ('man', 'Hombre'),
        ('woman', 'Mujer'),
    )

    # El nombre viene del campo "nombre", excepto:
    # PoblaconesAfectadas.descripcion

    name = models.CharField(max_length=255)
    is_name_created = models.BooleanField(default=False)
    # Al final del script, utilizando Capital.filial:
    # Si no existe, crear un nuevo actor solo con ese nombre,
    # y ponerle is_only_filial = True
    parent_actor = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    is_only_filial = models.BooleanField(default=False)
    # Capital.nacionalidad
    countries = models.ManyToManyField(Country, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    geo_reach = models.CharField(
        max_length=15, choices=GEO_REACH_CHOICES, blank=True, null=True)
    vulnerabilities = models.ManyToManyField(Vulnerability, blank=True)
    capital_type = models.ForeignKey(
        CapitalType, on_delete=models.CASCADE, blank=True, null=True)
    # Acá se irán los siguientes campos de Capital:
    # directores, inversionistas, is_cotiza_bolsa,
    # (no crear key si el campo está vacío)
    capital_extension = JSONField(blank=True, null=True)
    sex = models.CharField(
        max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    # True cuando Opositor.mujer tiene valor y su id es mayor o igual a 2
    is_woman_special = models.BooleanField(
        default=False, verbose_name='Participación sobresaliente de mujeres')
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Actor'
        verbose_name_plural = 'Actores'


class Participant(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, blank=True, null=True)
    participant_types = models.ManyToManyField(ParticipantType, blank=True)
    # Los campos origen de Actor tienen esto:
    # Capital
    interests = models.TextField(
        blank=True, null=True, verbose_name='Intereses (extensión)')

    def __str__(self):
        return self.actor

    class Meta:
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'


# ======================== VERSIÓN 1: ========================================
# --------------------- Capitalistas (actores) -------------------------------

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
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    matriz = models.TextField(blank=True, null=True)
    filial = models.TextField(blank=True, null=True)
    directores = models.TextField(blank=True, null=True)
    inversionistas = models.TextField(blank=True, null=True)
    nacionalidad = models.TextField(blank=True, null=True)
    # RICK: Aún no sé cómo voy a clasificar este campo
    is_capital_publico = models.BooleanField(blank=True, null=True)
    is_cotiza_bolsa = models.BooleanField(blank=True, null=True)
    interes = models.TextField(blank=True, null=True)
    # CAMPO VACÍO
    is_activo = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    instituciones_a_favor_proyecto = models.TextField(blank=True, null=True)
    instituciones_mediadoras = models.TextField(blank=True, null=True)
    instituciones_atienden_reclamos = models.TextField(blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.proyecto.nombre or str(self.pk)

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
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nombre = models.TextField(blank=True, null=True)
    forma_organizacion = models.ForeignKey(
        FormaOrganizacion, on_delete=models.CASCADE, blank=True, null=True)
    is_indigena = models.BooleanField(blank=True, null=True)
    pueblo_indigena = models.TextField(blank=True, null=True)
    is_campesino_or_comunero_or_ejidatario = models.BooleanField(
        blank=True, null=True)
    # RICK: Aún no sé qué vamos a hacer con este campo
    mujer = models.ForeignKey(
        Mujer, on_delete=models.CASCADE, blank=True, null=True)
    is_trabajador_empresa = models.BooleanField(blank=True, null=True)
    otros_opositores = models.TextField(blank=True, null=True)
    is_habitante_zona = models.BooleanField(blank=True, null=True)

    proyectos = models.ManyToManyField(
        Proyecto, db_table='ocs.opositores_to_proyecto', blank=True)
    notas = models.ManyToManyField(
        Nota, db_table='ocs.opositores_to_notas', blank=True)
    ubicaciones = models.ManyToManyField(
        Ubicacion, db_table='ocs.opositores_to_ubicaciones', blank=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    opositor = models.ForeignKey(
        Opositor, on_delete=models.CASCADE, blank=True, null=True)
    interes = models.TextField(blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.opositor, self.pk)

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
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    # CAMPO VACÍO
    id_subpoblacion_af = models.IntegerField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

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
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    poblacion_afectada = models.ForeignKey(
        PoblacionAfectada, on_delete=models.CASCADE, blank=True, null=True)
    subpoblacion_afectada = models.ForeignKey(
        SubpoblacionAfectada, on_delete=models.CASCADE, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    interes = models.TextField(blank=True, null=True)
    ubicacion = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.poblacion_afectada, self.pk)

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
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    poblacion_afectada = models.ForeignKey(
        PoblacionAfectada, on_delete=models.CASCADE, blank=True, null=True)
    interes = models.TextField(blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.poblacion_afectada, self.pk)

    class Meta:
        verbose_name = 'Interés Población'
        verbose_name_plural = 'Intereses Poblaciones'
        db_table = 'intereses_poblacion'


# CREATE TABLE ocs.grupos_apoyo (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_grupo_apoyo text,
#     nombre text,
#     interes text
# );

class GruposApoyo(models.Model):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_grupo_apoyo = models.TextField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    interes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        verbose_name = 'Grupo Apoyo'
        verbose_name_plural = 'Grupos Apoyo'
        db_table = 'grupos_apoyo'
