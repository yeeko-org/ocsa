from django.db import models

from source.models import Nota, Note, Mention
from project.models import Proyecto, Project
from space_time.models import Ubicacion, Temporalidad, Country
from django.db.models import JSONField
from utils.obj_str import nombre_or_pk
# from work_flux.models import StatusRegister


# Estos se generan al inicio, con los campos: (name, position, required_interests)
init_participant_types = [
    ('Promotor', 'support', False),
    ('Financiador', 'support', False),
    ('Represor', 'support', False),
    # Los GruposApoyo que tengan "Empresa" en el campo tipo_grupo_apoyo
    ('Partidario', 'support', False),
    # los que tengan not null Estado.instituciones_medidoras:
    ('Mediador', 'neutral', True),
    ('Analista', 'neutral', False),
    # los que tengan not null Estado.instituciones_atienden_reclamos:
    ('Atención a reclamos', 'neutral', False),
    # Los GruposApoyo que tengan "Opositor" u "Opositores" en tipo_grupo_apoyo
    ('Acompañante solidario', 'oppose', True),  # Acompañamiento-apoyo (representante) con los afectados u opositores
    ('Opositor', 'oppose', True),
    ('Otro', 'other', True),

    # RICK: Parece una categoría distinta:
    ('Ejecutor del Proyecto', 'support', False),
    # RICK: Parece que es lo mismo que el campo "is_affected"
    ('Beneficiario', 'support', True),

]

# estos se deben agregar también, pero con is_temporal = True
# Los grupos Opositores y PoblacionesAfectadas deben ir directo en su grupo
# Estado tiene su filtro específico y se agregan otros_opositores de Opositores
temporal_participant_types = [
    ('Capital', 'support', False),
    ('Opositores', 'oppose', True),
    ('PoblacionesAfectadas', 'oppose', True),
    # solo los que tengan not null Estado.instituciones_a_favor_proyecto
    ('Estado', 'support', False),
    # Estos se van a sacar de la tabla Opositores.otros_opositores, pero no
    # se le van a asignar todos los campos (solo su relación con nota y proyecto)
    ("otros_opositores", 'oppose', True),
]

POSITION_CHOICES = (
    ('undefined', 'No definido'),
    ('maybe_support', 'Posiblemente a favor'),
    ('support', 'A favor'),
    ('oppose', 'En contra'),
    ('neutral', 'Neutral'),
    ('other', 'Otro'),
)


class ParticipantType(models.Model):

    name = models.CharField(max_length=255)
    position = models.CharField(
        max_length=10, choices=POSITION_CHOICES, default='undefined')
    required_interests = models.BooleanField(
        default=True, verbose_name='Se requerirá que se agreguen intereses')
    is_temporal = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Participación en Proyecto'
        verbose_name_plural = 'Tipos de Participación en Proyecto'


# en Actor están especificados los 6 posibles valores
# LUCIAN: He identificado 6 campos, pueden estar en Actor o acá, ¿qué piensas?
class Belong(models.Model):
    # LUCIAN, esto se va a usar para la equivalencia de los campos
    key_name = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # is_indigenous = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Vulnerabilidad'
        verbose_name_plural = 'Vulnerabilidades'


class IndigenousGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Indígena'
        verbose_name_plural = 'Grupos Indígenas'


class SectorGroup(models.Model):
    name = models.CharField(max_length=255)
    is_collective = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Sectorial'
        verbose_name_plural = 'Grupos Sectoriales'


# Esto se alimentará de:
# cat_forma_organizacion: todos tendrán el sector con nombre "Varios",
#   y con is_collective = True
class Sector(models.Model):
    name = models.CharField(max_length=255)
    needs_name = models.BooleanField(default=False)
    sector_group = models.ForeignKey(
        SectorGroup, on_delete=models.CASCADE)
    common_participant_types = models.ManyToManyField(
        ParticipantType, blank=True)
    has_belongs = models.BooleanField(default=True)
    common_belongs = models.ManyToManyField(
        Belong, blank=True)

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
    # PoblacionesAfectadas.descripcion, en este caso, hay varios registros
    # que tienen comillas, están raros, parecen como no terminados,
    # en esos casos, habrá que poner el campo is_incomplete = True
    # Estado, que tiene 3 campos y su comportamiento se explica arrriba
    name = models.CharField(max_length=255)
    is_incomplete = models.BooleanField(default=False)
    is_name_created = models.BooleanField(default=False)
    # Al final del script, utilizando Capital.matriz:
    # Si no existe, crear un nuevo actor solo con ese nombre,
    # y ponerle is_only_related = True
    # Por el contrario, con el campo de Capital.filial se creará un nuevo actor
    # cuyo parent_actor será el registro actual
    parent_actor = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    is_only_related = models.BooleanField(default=False)
    # Capital.nacionalidad
    countries = models.ManyToManyField(Country, blank=True)
    sector = models.ForeignKey(
        Sector, on_delete=models.CASCADE, blank=True, null=True)
    sector_name = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name='Nombre del sector (opcional)')
    geo_reach = models.CharField(
        max_length=15, choices=GEO_REACH_CHOICES, blank=True, null=True)

    # Pertenencia a partir de campos de la tabla Opisitores y a partir de
    # los nombres de PoblacionesAfectadas.poblacion_afectada.nombre

    # is_indigena => Indígena
    # Opositores: campo is_indigena == True
    # PoblacionesAfectadas: name == "Indígena"

    # is_farmer => Campesino
    # Opositores: campo is_campesino_or_comunero_or_ejidatario == True
    # PoblacionesAfectadas: name == "Campesino/Comunero/Ejidatario"

    # is_worker => Trabajador
    # Opositores: campo is_trabajador_empresa == True
    # PoblacionesAfectadas: name == "Trabajadores de la empresa"

    # is_habitant => Habitante
    # Opositores: campo is_habitante_zona == True
    # PoblacionesAfectadas: name == "Pobladores" or name == "Vecinos"

    # is_woman_special => Mujer
    # Esto se construye a partir de Opositor.mujer,
    # cuando Opositor.mujer tiene valor y su id es mayor o igual a 2;
    #
    # "is_affected" => Población Afectada
    # Todos los de la tabla PopulacionesAfectadas tendrán este campo
    belongs = models.ManyToManyField(Belong, blank=True)

    # Construído a partir de;
    # Opositores.pueblo_indigena
    # PoblacionesAfectadas.subpoblacion_afectada >-- cat_subpoblacion_afectada
    # cuando el id > 4 ; también agregar su belong de "is_indigena"
    indigenous_group = models.ForeignKey(
        IndigenousGroup, on_delete=models.CASCADE, blank=True, null=True)
    capital_type = models.ForeignKey(
        CapitalType, on_delete=models.CASCADE, blank=True, null=True)

    # Acá se irán los siguientes campos de Capital, como diccionario:
    # directores, inversionistas, is_cotiza_bolsa,
    # (no crear key si el campo está vacío)
    capital_extension = JSONField(blank=True, null=True)
    sex = models.CharField(
        max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    # True cuando Opositor.mujer tiene valor y su id es mayor o igual a 2
    # status_register = models.ForeignKey(
    #     'work_flux.StatusRegister', on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Actor'
        verbose_name_plural = 'Actores'


# La forma de vincular las menciones y los participantes es directo casi
# siempre relativamente 'directa' (con nota y proyecto):
# Capital, Estado, PoblacionesAfectadas, GruposApoyo
# Caso de Opositores: se debe hacer no solo con "opositores_to_notas" (ManyToMany)
# y "opositores_to_proyecto" (ManyToMany),
# sino también con InteresesOpositores, que tiene Opositor, proyecto y nota
class Participant(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True)
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, blank=True, null=True)
    participant_types = models.ManyToManyField(ParticipantType, blank=True)
    # raw_interests = models.TextField(
    #     blank=True, null=True, verbose_name='Intereses (extensión)')

    def __str__(self):
        return self.actor

    class Meta:
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'


INTEREST_CLUSTERS = [
    ('denuncia', 'Denuncia'),
    # ('reclamo', 'Reclamo'),
    ('demanda', 'Demanda'),
    ('otro', 'Otro'),
]


class InterestGroup(models.Model):
    cluster = models.CharField(
        max_length=20, choices=INTEREST_CLUSTERS, default='otro')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    participant_types = models.ManyToManyField(
        ParticipantType, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Agrupador de tipos de interés'
        verbose_name_plural = 'Agrupadores de tipos de interés'


class InterestType(models.Model):
    group = models.ForeignKey(
        InterestGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Interés'
        verbose_name_plural = 'Tipos de Interés'


# En algunos casos, esto provendrá de una relación 1:1, a veces M:1,
# pero vamos a estandarizar siempre a M:1 a través de Interest
# Los campos origen de Actor tienen esto:
# Capital.interes, PoblacionesAfectadas.interes, GruposApoyo.interes
# Opositores a través de InteresesOpositores (m:m), parece algo complejo!!
# Estado no tiene interés

class Interest(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    interest_type = models.ForeignKey(
        InterestType, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text or str(self.pk)

    class Meta:
        verbose_name = 'Interés'
        verbose_name_plural = 'Intereses'


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
    # RICK: No me queda claro qué haremos con este campo
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
    # RICK Y LUCIAN: Aún no le encuentro sentido a este campo
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.proyecto or str(self.pk)

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

class Opositores(models.Model):
    nombre = models.TextField(blank=True, null=True)
    forma_organizacion = models.ForeignKey(
        FormaOrganizacion, on_delete=models.CASCADE, blank=True, null=True)
    # RICK: Aún no sé qué vamos a hacer con este campo
    mujer = models.ForeignKey(
        Mujer, on_delete=models.CASCADE, blank=True, null=True)
    is_campesino_or_comunero_or_ejidatario = models.BooleanField(
        blank=True, null=True)
    is_trabajador_empresa = models.BooleanField(blank=True, null=True)
    is_habitante_zona = models.BooleanField(blank=True, null=True)
    is_indigena = models.BooleanField(blank=True, null=True)
    pueblo_indigena = models.TextField(blank=True, null=True)
    otros_opositores = models.TextField(blank=True, null=True)
    proyectos = models.ManyToManyField(
        Proyecto, db_table='ocs.opositores_to_proyecto', blank=True)
    notas = models.ManyToManyField(
        Nota, db_table='ocs.opositores_to_notas', blank=True)
    # RICK: Falta decidir el comportamiento de este campo
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
        Opositores, on_delete=models.CASCADE, blank=True, null=True)
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
    # RICK: Falta decidir el comportamiento de este campo
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

# TABLA VACÍA
class InteresesPoblacion(models.Model):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    # RICK Y LUCIAN: Este campo parece repetido, similar a nota y proyecto
    # ¿Qué podríamos hacer para mantener la congruencia?
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
