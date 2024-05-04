from .models import init_participant_types, temporal_participant_types, ParticipantType

class ParticipantTypes:
    for name, position, required_interests in init_participant_types:
        ParticipantType.objects.get_or_create(
            name=name, position=position, required_interests=required_interests
        )

class TemporalParticipantTypes:
    for name, position, required_interests in temporal_participant_types:
        ParticipantType.objects.get_or_create(
            name=name,
            position=position,
            required_interests=required_interests,
            is_temporal=True
        )