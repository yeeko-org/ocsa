from rest_framework import serializers

from classify.models import (
    ParticipantType,
    Belong,
    IndigenousGroup,
    SectorGroup,
    Sector,
    InterestGroup,
    InterestType
)
from event.models import (
    EventGroup,
    EventType,
    EventSubtype,
    EventRole,)

from impact.models import ImpactSubtype, ImpactType
from profile_auth.models import Role
from source.models import Source
from work_flux.models import StatusControl

from space_time.models import StatusProject


class StatusProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusProject
        fields = "__all__"


class StatusControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusControl
        fields = "__all__"


class ParticipantTypeSerializer(serializers.ModelSerializer):
    status_validation = StatusControlSerializer()

    class Meta:
        model = ParticipantType
        fields = "__all__"


class BelongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Belong
        fields = "__all__"


class IndigenousGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndigenousGroup
        fields = "__all__"


class SectorGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorGroup
        fields = "__all__"


class SectorSerializer(serializers.ModelSerializer):
    sector_group = SectorGroupSerializer()
    common_participant_types = ParticipantTypeSerializer(many=True)
    common_belongs = BelongSerializer(many=True)
    status_validation = StatusControlSerializer()

    class Meta:
        model = Sector
        fields = "__all__"


class InterestGroupSerializer(serializers.ModelSerializer):
    participant_types = ParticipantTypeSerializer(many=True)

    class Meta:
        model = InterestGroup
        fields = "__all__"


class InterestTypeSerializer(serializers.ModelSerializer):
    group = InterestGroupSerializer()

    class Meta:
        model = InterestType
        fields = "__all__"


class EventGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGroup
        fields = "__all__"


class EventTypeSerializer(serializers.ModelSerializer):
    group = EventGroupSerializer()
    status_validation = StatusControlSerializer()

    class Meta:
        model = EventType
        fields = "__all__"


class EventSubtypeSerializer(serializers.ModelSerializer):
    event_types = EventTypeSerializer(many=True)
    status_validation = StatusControlSerializer()

    class Meta:
        model = EventSubtype
        fields = "__all__"


class EventRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRole
        fields = "__all__"


class ImpactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactType
        fields = "__all__"


class ImpactSubtypeSerializer(serializers.ModelSerializer):
    impact_type = ImpactTypeSerializer()

    class Meta:
        model = ImpactSubtype
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"
