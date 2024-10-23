from rest_framework import serializers

from classify.models import (
    ParticipantType,
    ParticipantGroup,
    Belong,
    IndigenousGroup,
    SectorGroup,
    Sector,
    InterestGroup,
    InterestType,
    InterestSubtype,
)


class ParticipantTypeSerializer(serializers.ModelSerializer):
    # status_validation = StatusControlSerializer()

    class Meta:
        model = ParticipantType
        fields = "__all__"


class ParticipantGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipantGroup
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
    # sector_group = SectorGroupSerializer()
    # common_participant_types = ParticipantTypeSerializer(many=True)
    # common_belongs = BelongSerializer(many=True)
    # status_validation = StatusControlSerializer()

    class Meta:
        model = Sector
        fields = "__all__"


class InterestGroupSerializer(serializers.ModelSerializer):
    # participant_types = ParticipantTypeSerializer(many=True)

    class Meta:
        model = InterestGroup
        fields = "__all__"


class InterestTypeSerializer(serializers.ModelSerializer):
    # group = InterestGroupSerializer()

    class Meta:
        model = InterestType
        fields = "__all__"


class InterestSubtypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterestSubtype
        fields = "__all__"
