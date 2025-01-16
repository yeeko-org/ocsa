from work_flux.models import StatusControl
from classify.models import (
    ParticipantType, Belong, SectorGroup, Sector, ParticipantGroup,
    InterestGroup, InterestType, InterestSubtype)

init_participant_groups = {
    "oppose": {
        "icon": "record_voice_over", "color": "lime", "order": 1,
        "name": "En contra"
    },
    "neutral": {
        "icon": "gavel", "color": "blue-grey""", "order": 2,
        "name": "Neutral"
    },
    "support": {
        "icon": "thumb_up", "color": "teal", "order": 3,
        "name": "A favor"
    },
    "other": {
        "icon": "help", "color": "black", "order": 5,
        "name": "Otro"
    }
}


class InitParticipantGroups:

    def __init__(self):
        for position, data in init_participant_groups.items():
            ParticipantGroup.objects.get_or_create(
                key_name=position,
                name=data["name"],
                defaults={
                    "description": "",
                    "icon": data["icon"],
                    "order": data["order"],
                    "color": data["color"]
                }
            )


class ParticipantTypes:
    def __init__(self):

        # Estos se generan al inicio, con los campos: (name, position, required_interests)
        init_participant_types = [
            ('Financiador', 'support', False, 31),
            ('Partidario', 'support', False, 32),
            ('Represor', 'support', False, 34),
            ('Promotor', 'support', False, 36),
            ('Mediador', 'neutral', True, 20),
            ('Analista', 'neutral', False, 25),
            ('Atención a reclamos', 'neutral', False, 22),
            # Los GruposApoyo que tengan "Opositor" u "Opositores" en tipo_grupo_apoyo
            # Acompañamiento-apoyo (representante) con los afectados u opositores
            ('Acompañante solidario', 'oppose', True, 3),
            ('Opositor', 'oppose', True, 1),
            ('Otro', 'other', True, 51),

            # RICK: Parece una categoría distinta:
            ('Ejecutor del Proyecto', 'support', False, 38),
            # RICK: Parece que es lo mismo que el campo "is_affected"
            ('Beneficiario', 'support', True, 39),
            # ("Por definir (de violencias)", 'oppose', False),
        ]
        for name, position, required_interests, order in init_participant_types:
            participant_group = ParticipantGroup.objects.get(
                key_name=position)
            pt, created = ParticipantType.objects.get_or_create(
                name=name, position=position)
            pt.order = order
            pt.required_interests = required_interests
            pt.participant_group = participant_group
            pt.save()


class TemporalParticipantTypes:
    def __init__(self):
        # estos se deben agregar también, pero con is_temporal = True
        # Los grupos Opositores y PoblacionesAfectadas deben ir directo en su grupo
        # Estado tiene su filtro específico y se agregan otros_opositores de Opositores
        temporal_participant_types = [
            ('Capital', 'support', False, 41),
            # ('Opositores', 'oppose', True, 10),
            ('PoblacionesAfectadas', 'oppose', True, 11),
            ('Estado', 'support', False, 42),
            ("Por definir (de violencias)", 'other', False, 50),
            # Estos se van a sacar de la tabla Opositores.otros_opositores, pero no
            # se le van a asignar todos los campos (solo su relación con nota y proyecto)
            ("otros_opositores", 'oppose', True, 12),
        ]

        for name, position, required_interests, order in temporal_participant_types:
            participant_group = ParticipantGroup.objects.get(
                key_name=position)
            pt, _ = ParticipantType.objects.get_or_create(
                name=name,
                position=position,
                status_validation_id="need_reclassify",
            )
            pt.order = order
            pt.required_interests = required_interests
            pt.participant_group = participant_group
            pt.save()


class InitSectorGroups:
    def __init__(self):
        init_sector_groups = [
            ('Individuos', False, None, 'face', 8),
            ('Empresas privadas', True, 'private', 'business', 1),
            ('Empresas estatales', True, 'public', 'assured_workload', 2),
            ('Estado', True, 'public', 'account_balance', 3),
            ('Sociedad Civil', True, None, 'groups', 4),
            ('Organizaciones Internacionales', True, None, 'public', 6),
            ('Grupos no organizados', True, None, 'groups', 7),
            ('Universidades', True, None, 'school', 5),
            ('Contradictorio', True, 'conflict', 'report', 25),
            ('Varios', True, None, 'report_problem', 26),
            ('Individuos (Varios)', False, None, 'groups', 27),
        ]
        for name, is_collective, capital_type, icon, order in init_sector_groups:
            SectorGroup.objects.get_or_create(
                name=name,
                is_collective=is_collective,
                capital_type=capital_type,
                defaults={
                    'icon': icon,
                    'order': order
                }
            )


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
    ('Empresariado', False, 'Individuos', False),
    ('Institución del Estado', False, 'Estado', 'could_reclassify'),
    ('Responsable No Estatal', False, 'Varios', 'could_reclassify'),
    ('Contradictorio', False, 'Contradictorio', 'need_reclassify'),
    ('Varios', False, 'Varios', 'need_reclassify'),
]


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
            ('is_worker', 'Trabajador', 'engineering'),
            ('is_affected', 'Afectado', 'affected'),
            ('is_habitant', 'Habitante', 'cottage'),
            ('is_indigena', 'Indígena', 'groups_2'),
            ('is_farmer', 'Campesino', 'agriculture'),
            ('is_urban', 'Urbano', 'location_city'),
            ('is_leader', 'Líder', 'admin_panel_settings'),
            ('is_women_special', 'Participación sobresaliente de mujeres', 'woman'),
            ('is_woman_organization', 'Organización de mujeres', 'diversity_1'),
            ('has_protection', 'Tiene Protección', 'security'),
        ]
        for key_name, value, icon in init_belongs:
            if Belong.objects.filter(key_name=key_name).exists():
                continue
            Belong.objects.get_or_create(
                key_name=key_name,
                name=value,
                icon=icon
            )


class InitInterestTypes:

    def __init__(self):

        # InterestGroup.objects.get_or_create(
        #     name="Denuncia", defaults={"icon": "report", "order": 1})
        # InterestGroup.objects.get_or_create(
        #     name="Reclamo", defaults={"icon": "gavel", "order": 2})
        undefined_ig, _ = InterestGroup.objects.get_or_create(
            name="general",
            defaults={"icon": "front_hand", "order": 3, "color": "grey"})
        undefined_ig_it, _ = InterestType.objects.get_or_create(
            name="general",
            interest_group=undefined_ig,
            defaults={
                "order": 1,
                "status_validation_id": "need_reclassify"
            }
        )
        InterestSubtype.objects.get_or_create(
            name="general",
            interest_type=undefined_ig_it,
            defaults={
                "order": 1,
                "status_validation_id": "need_reclassify"
            }
        )



