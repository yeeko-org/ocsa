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
                is_temporal=True
            )


class InitSectorGroups:
    def __init__(self):
        for name, is_collective in init_sector_groups:
            SectorGroup.objects.get_or_create(
                name=name, is_collective=is_collective)

