from work_flux.models import StatusControl
from classify.models import ParticipantType, Belong, \
    init_sector_groups, SectorGroup, init_sectors, Sector


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


class ParticipantTypes:
    def __init__(self):
        for name, position, required_interests in init_participant_types:
            ParticipantType.objects.get_or_create(
                name=name, position=position, required_interests=required_interests
            )


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


class TemporalParticipantTypes:
    def __init__(self):
        for name, position, required_interests in temporal_participant_types:
            ParticipantType.objects.get_or_create(
                name=name,
                position=position,
                required_interests=required_interests,
                status_validation_id="need_reclassify"
            )


class InitSectorGroups:
    def __init__(self):
        for name, is_collective, capital_type in init_sector_groups:
            SectorGroup.objects.get_or_create(
                name=name,
                is_collective=is_collective,
                capital_type=capital_type
            )


class InitSector:
    def __init__(self):
        for name, needs_name, sector_group_name, status_validation_name in init_sectors:
            sector_group, _ = SectorGroup.objects.get_or_create(
                name=sector_group_name)

            if Sector.objects.filter(name=name).exists():
                continue

            if status_validation_name:
                try:
                    status_validation = StatusControl.objects.get(
                        name=status_validation_name)
                except StatusControl.DoesNotExist:
                    status_validation = StatusControl.objects.create(
                        name=status_validation_name,
                        public_name=status_validation_name
                    )
            else:
                status_validation = None

            Sector.objects.create(
                name=name,
                needs_name=needs_name,
                sector_group=sector_group,
                status_validation=status_validation
            )


class InitBelongs:
    def __init__(self):
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
        for key_name, value in init_belongs:
            if Belong.objects.filter(key_name=key_name).exists():
                continue
            Belong.objects.get_or_create(
                key_name=key_name,
                name=value
            )
