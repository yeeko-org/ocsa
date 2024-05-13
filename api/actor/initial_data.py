from .models import (
    init_participant_types, temporal_participant_types, ParticipantType,
    init_sector_groups, SectorGroup)


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



