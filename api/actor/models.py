from django.db import models

from source.models import Mention
from space_time.models import Country
from django.db.models import JSONField
from work_flux.models import StatusControl
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
    # Acompañamiento-apoyo (representante) con los afectados u opositores
    ('Acompañante solidario', 'oppose', True),
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
    ("Por definir (de violencias)", 'undefined', False),
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
        max_length=14, choices=POSITION_CHOICES, default='undefined')
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


init_sector_groups = [
    ('Individuos', False),
    ('Empresas Privadas', True),
    ('Empresas estatales', True),
    ('Empresas privadas', True),
    ('Estado', True),
    ('Contradictorio', True),
    ('Varios', True),
]


class SectorGroup(models.Model):
    name = models.CharField(max_length=255)
    is_collective = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Sectorial'
        verbose_name_plural = 'Grupos Sectoriales'


init_sectors = [
    ('Empresa privada nacional', False, 'Empresas Privadas', None),
    ('Empresa privada extranjera', False, 'Empresas Privadas', None),
    ('Empresa privada', False, 'Empresas Privadas', 'need_reclassify'),
    ('Empresa estatal', False, 'Empresas estatales', None),
    ('Poder Ejecutivo Federal', False, 'Estado', None),
    ('Poder Ejecutivo Estatal', False, 'Estado', None),
    ('Poder Ejecutivo Municipal', False, 'Estado', None),
    ('Poder Judicial', False, 'Estado', None),
    ('Poder Legislativo', False, 'Estado', None),
    ('Institución del Estado', False, 'Estado', 'need_reclassify'),
    ('Contradictorio', False, 'Contradictorio', 'need_reclassify'),
    ('Varios', False, 'Varios', 'need_reclassify'),
    ('Empresariado', False, 'Individuos', False),
]


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
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'


def default_list():
    return []


CAPITAL_TYPES = (
    ('public', 'Público'),
    ('private', 'Privado'),
    ('mixed', 'Mixto'),
    ("conflict", "Conflicto"),
)


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
    official_name = models.CharField(
        max_length=255, blank=True, null=True)
    std_name = models.CharField(
        max_length=255, blank=True, null=True)
    alternative_names = models.JSONField(
        default=default_list, blank=True, null=True)
    is_incomplete = models.BooleanField(default=False)
    is_name_created = models.BooleanField(default=False)

    # Al final del script, utilizando Capital.matriz:
    # Si no existe, crear un nuevo actor solo con ese nombre,
    # y ponerle is_only_related = True
    # Por el contrario, con el campo de Capital.filial se creará un nuevo actor
    # cuyo parent_actor será el registro actual
    parent_actor = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    is_only_related = models.BooleanField(blank=True, null=True)

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
    capital_type = models.CharField(
        max_length=10, choices=CAPITAL_TYPES, blank=True, null=True)

    # Acá se irán los siguientes campos de Capital, como diccionario:
    # directores, inversionistas, is_cotiza_bolsa,
    # (no crear key si el campo está vacío)
    capital_extension = JSONField(blank=True, null=True)
    # True cuando Opositor.mujer tiene valor y su id es mayor o igual a 2
    sex = models.CharField(
        max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    capital_id_ref = models.IntegerField(blank=True, null=True)

    def add_comment(self, comment: str):
        if not comment:
            return
        if self.comments:
            if comment not in self.comments:
                self.comments += f"\n\n{comment}"
        else:
            self.comments = comment
        self.save()

    def append_alternative_name(self, name, save=True):
        if not name or self.name == name:
            return

        if not isinstance(self.alternative_names, list):
            self.alternative_names = []

        if name not in self.alternative_names:
            self.alternative_names.append(name)
            if save:
                self.save()

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
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE)
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
        InterestType, on_delete=models.CASCADE, blank=True, null=True)

    text = models.TextField()

    def __str__(self):
        return self.text or str(self.pk)

    class Meta:
        verbose_name = 'Interés'
        verbose_name_plural = 'Intereses'


LEGACY_MODELS = (
    ('Capital', 'Capital'),
    ('Estado', 'Estado'),
    ('Opositores', 'Opositores'),
    ('Poblacione', 'PoblacionesAfectadas'),
    ('GruposApoyo', 'GruposApoyo'),
)


class OriginReference(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    type_model = models.CharField(max_length=20, choices=LEGACY_MODELS)
    origin_id = models.IntegerField()
    actor_created = models.BooleanField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin_id} - {self.type_model}"

    class Meta:
        verbose_name = 'Referencia de Origen'
        verbose_name_plural = 'Referencias de Origen'
