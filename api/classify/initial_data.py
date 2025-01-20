from work_flux.models import StatusControl
from classify.models import (
    ParticipantType, Belong, SectorGroup, Sector, ParticipantGroup,
    InterestGroup, InterestType, InterestSubtype)


class InitParticipantGroups:

    def __init__(self):

        init_participant_groups = {
            "oppose": {
                "icon": "record_voice_over", "color": "lime", "order": 1,
                "name": "En contra"
            },
            "neutral": {
                "icon": "gavel", "color": "blue-grey", "order": 2,
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


class InitParticipantTypes:
    def __init__(self):

        # Estos se generan al inicio, con los campos: (name, position, required_interests)
        init_participant_types = [
            ('Financiador', 'support', False, 31, 'proposed'),
            ('Partidario', 'support', False, 32, 'yk_proposed'),
            ('Represor', 'support', False, 34, 'proposed'),
            ('Promotor', 'support', False, 36, 'proposed'),
            ('Mediador', 'neutral', True, 20, 'yk_proposed'),
            ('Analista', 'neutral', False, 25, 'yk_proposed'),
            ('Atención a reclamos', 'neutral', False, 22, 'yk_proposed'),
            # Los GruposApoyo que tengan "Opositor" u "Opositores" en tipo_grupo_apoyo
            # Acompañamiento-apoyo (representante) con los afectados u opositores
            ('Acompañante solidario', 'oppose', True, 3, 'yk_proposed'),
            ('Opositor', 'oppose', True, 1, 'original'),
            ('Otro', 'other', True, 51, 'proposed'),

            # RICK: Parece una categoría distinta:
            ('Ejecutor del Proyecto', 'support', False, 38, 'proposed'),
            # RICK: Parece que es lo mismo que el campo "is_affected"
            ('Beneficiario', 'support', True, 39, 'proposed'),
            # ("Por definir (de violencias)", 'oppose', False),
        ]
        # TODO QUICK Comentado:
        # for data in init_participant_types:
        #     name, position, required_interests, order, st_validation = data
        #     participant_group = ParticipantGroup.objects.get(
        #         key_name=position)
        #     pt, created = ParticipantType.objects.get_or_create(
        #         name=name, position=position)
        #     pt.order = order
        #     pt.required_interests = required_interests
        #     pt.participant_group = participant_group
        #     pt.status_validation_id = st_validation
        #     pt.save()


class TemporalParticipantTypes:
    def __init__(self):
        # estos se deben agregar también, pero con is_temporal = True
        # Los grupos Opositores y PoblacionesAfectadas deben ir directo en su grupo
        # Estado tiene su filtro específico y se agregan otros_opositores de Opositores
        temporal_participant_types = [
            ('Capital', 'support', False, 41, ''),
            # ('Opositores', 'oppose', True, 10),
            ('PoblacionesAfectadas', 'oppose', True, 11, ''),
            ('Estado', 'support', False, 42, ''),
            ("Por definir (de violencias)", 'other', False, 50, ''),
            # Estos se van a sacar de la tabla Opositores.otros_opositores, pero no
            # se le van a asignar todos los campos (solo su relación con nota y proyecto)
            ("otros_opositores", 'oppose', True, 12, ''),
        ]

        # TODO QUICK Comentado:
        # for data in temporal_participant_types:
        #     name, position, required_interests, order, description = data
        #     participant_group = ParticipantGroup.objects.get(
        #         key_name=position)
        #     # comments = ("YEEKO: Es una categoría previa (v.1) pero"
        #     #             "deberíamos reclasificar estos actores")
        #     pt, _ = ParticipantType.objects.get_or_create(
        #         name=name,
        #         position=position,
        #         status_validation_id="need_reclassify",
        #         description=description,
        #         # comments=comments
        #     )
        #     pt.order = order
        #     pt.required_interests = required_interests
        #     pt.participant_group = participant_group
        #     pt.save()


init_sector_groups = [
    ('Individuos', False, None, 'face', 8, 'yk_proposed'),
    ('Empresas privadas', True, 'private', 'business', 1, 'yk_proposed'),
    ('Empresas estatales', True, 'public', 'assured_workload', 2, 'yk_proposed'),
    ('Estado', True, 'public', 'account_balance', 3, 'yk_proposed'),
    ('Sociedad Civil', True, None, 'groups', 4, 'proposed'),
    ('Organizaciones Internacionales', True, None, 'public', 6, 'proposed'),
    ('Grupos no organizados', True, None, 'groups', 7, 'proposed'),
    ('Universidades', True, None, 'school', 5, 'proposed'),
    ('Grupos Delictivos', True, None, 'groups', 9, 'proposed'),
    ('Otros', None, None, 'groups_3', 15, 'yk_proposed'),
    # ('Contradictorio', True, 'conflict', 'report', 31),
    # ('Varios', True, None, 'report_problem', 26),
    ('Otros por identificar', None, None, 'report_problem', 36, 'need_reclassify'),
    # ('Individuos (Varios)', False, None, 'groups', 37),
]


class InitSectorGroups:

    def __init__(self):
        for data in init_sector_groups:
            name, is_collective, capital_type, icon, order, st_validation_id = data
            SectorGroup.objects.get_or_create(
                name=name,
                capital_type=capital_type,
                defaults={
                    'is_collective': is_collective,
                    'icon': icon,
                    'order': order,
                    'status_validation_id': st_validation_id
                }
            )


init_sectors = [
    ('Empresariado', 'Individuos', 'yk_proposed'),
    ('Empresa privada nacional', 'Empresas privadas', 'yk_proposed'),
    ('Empresa privada extranjera', 'Empresas privadas', 'yk_proposed'),
    ('Empresa privada', 'Empresas privadas', 'could_reclassify'),
    ('Empresa estatal', 'Empresas estatales', 'yk_proposed'),
    ('Poder Ejecutivo Federal', 'Estado', 'proposed'),
    ('Poder Ejecutivo Estatal', 'Estado', 'proposed'),
    ('Poder Ejecutivo Municipal', 'Estado', 'proposed'),
    ('Poder Judicial', 'Estado', 'proposed'),
    ('Poder Legislativo', 'Estado', 'proposed'),
    ('Institución del Estado', 'Estado', 'could_reclassify'),
    # ('Responsable No Estatal', 'Varios', 'could_reclassify'),
    ('Responsable No Estatal', 'Otros por identificar', 'could_reclassify'),
    ('Contradictorio', 'Otros por identificar', 'need_reclassify'),
    # ('Varios', 'Varios', 'need_reclassify'),
    ('No identificado', 'Otros por identificar', 'need_reclassify'),
    ('No identificado (individuos)', 'Otros por identificar', 'need_reclassify'),
]


class InitSector:
    def __init__(self):
        for data in init_sectors:
            name, sector_group_name, st_validation_id = data
            sector_group, _ = SectorGroup.objects.get_or_create(
                name=sector_group_name)

            if Sector.objects.filter(name=name).exists():
                continue

            if st_validation_id:
                try:
                    status_validation = StatusControl.objects.get(
                        name=st_validation_id)
                except StatusControl.DoesNotExist:
                    status_validation = StatusControl.objects.create(
                        name=st_validation_id,
                        public_name=st_validation_id
                    )
            else:
                status_validation = None

            Sector.objects.create(
                name=name,
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



