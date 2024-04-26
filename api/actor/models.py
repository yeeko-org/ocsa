from django.db import models

from source.models import Nota, Note
from project.models import Proyecto, Project
from space_time.models import Ubicacion, Temporalidad, Country
from django.db.models import JSONField
# from work_flux.models import StatusRegister


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

    name = models.CharField(max_length=255)
    is_name_created = models.BooleanField(default=False)
    parent_actor = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    countries = models.ManyToManyField(Country, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    geo_reach = models.CharField(
        max_length=15, choices=GEO_REACH_CHOICES, blank=True, null=True)
    vulnerabilities = models.ManyToManyField(Vulnerability, blank=True)
    capital_type = models.ForeignKey(
        CapitalType, on_delete=models.CASCADE, blank=True, null=True)
    capital_extension = JSONField(blank=True, null=True)
    sex = models.CharField(
        max_length=10, choices=SEX_CHOICES, blank=True, null=True)
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
