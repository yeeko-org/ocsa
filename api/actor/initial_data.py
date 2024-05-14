from work_flux.models import StatusControl
from .models import (
    Belong, Sector, init_participant_types, temporal_participant_types, ParticipantType,
    init_sector_groups, init_sectors, SectorGroup, init_belongs)


class ParticipantTypes:
    def __init__(self):
        for name, position, required_interests in init_participant_types:
            ParticipantType.objects.get_or_create(
                name=name, position=position, required_interests=required_interests
            )


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
        for key_name, value in init_belongs:
            if Belong.objects.filter(key_name=key_name).exists():
                continue
            Belong.objects.get_or_create(
                key_name=key_name,
                name=value
            )
