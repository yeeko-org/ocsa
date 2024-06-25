from django.db import models

from work_flux.models import StatusControl

# Estos se generan al inicio, con los campos: (name, position, required_interests)
init_participant_types = [
    ('Promotor', 'support', False),
    ('Financiador', 'support', False),
    ('Represor', 'support', False),
    ('Partidario', 'support', False),
    ('Mediador', 'neutral', True),
    ('Analista', 'neutral', False),
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
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Participación en Proyecto'
        verbose_name_plural = 'Tipos de Participación en Proyecto'


init_belongs = [
    ('is_worker', 'Trabajador'),
    ('is_affected', 'Afectado'),
    ('is_habitant', 'Habitante'),
    ('is_indigena', 'Indígena'),
    ('is_farmer', 'Campesino'),
    ('is_urban', 'Urbano'),
    ('is_leader', 'Líder'),
    ('is_women_special', 'Participación sobresaliente de mujeres'),
    ('is_woman_organization', 'Organización de mujeres'),
    ('has_protection', 'Tiene Protección'),
]


class Belong(models.Model):
    # LUCIAN, esto se va a usar para la equivalencia de los campos
    key_name = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo de Pertenencia (Vulnerabilidad)'
        verbose_name_plural = 'Grupos de Pertenencia (Vulnerabilidades)'


class IndigenousGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Indígena'
        verbose_name_plural = 'Grupos Indígenas'


init_sector_groups = [
    ('Individuos', False, None),
    ('Empresas privadas', True, 'private'),
    ('Empresas estatales', True, 'public'),
    ('Estado', True, 'public'),
    ('Contradictorio', True, 'conflict'),
    ('Varios', True, None),
    ('Individuos (Varios)', False, None),
]
CAPITAL_TYPES = (
    ('public', 'Público'),
    ('private', 'Privado'),
    ('mixed', 'Mixto'),
    ("conflict", "Conflicto"),
)


class SectorGroup(models.Model):
    name = models.CharField(max_length=255)
    is_collective = models.BooleanField(blank=True, null=True)
    has_belongs = models.BooleanField(default=True)
    capital_type = models.CharField(
        max_length=10, choices=CAPITAL_TYPES, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grupo Sectorial'
        verbose_name_plural = 'Grupos Sectoriales'


init_sectors = [
    ('Empresa privada nacional', False, 'Empresas privadas', None),
    ('Empresa privada extranjera', False, 'Empresas privadas', None),
    ('Empresa privada', False, 'Empresas privadas', 'could_reclassify'),
    ('Empresa estatal', False, 'Empresas estatales', None),
    ('Poder Ejecutivo Federal', False, 'Estado', None),
    ('Poder Ejecutivo Estatal', False, 'Estado', None),
    ('Poder Ejecutivo Municipal', False, 'Estado', None),
    ('Poder Judicial', False, 'Estado', None),
    ('Poder Legislativo', False, 'Estado', None),
    ('Institución del Estado', False, 'Estado', 'could_reclassify'),
    ('Responsable No Estatal', False, 'Varios', 'could_reclassify'),
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
    common_belongs = models.ManyToManyField(
        Belong, blank=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'


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
