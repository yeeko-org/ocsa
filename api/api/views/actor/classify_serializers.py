from api.views.actor import ActorBaseSerializer
from api.views.common_serializers import CommonCount
from classify.models import (
    IndigenousGroup, Sector, SectorGroup, ParticipantGroup, ParticipantType,
    Belong, Country)
from rest_framework import serializers


class IndigenousGroupSerializer(CommonCount):

    class Meta:
        model = IndigenousGroup
        fields = "__all__"


class IndigenousGroupFullSerializer(CommonCount):
    actors = ActorBaseSerializer(many=True, read_only=True)

    class Meta:
        model = IndigenousGroup
        fields = "__all__"


class SectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sector
        fields = "__all__"


class SectorFullSerializer(serializers.ModelSerializer):
    actors_count = serializers.ReadOnlyField()

    class Meta:
        model = Sector
        fields = "__all__"


class SectorGroupSerializer(serializers.ModelSerializer):
    sectors_count = serializers.ReadOnlyField()

    class Meta:
        model = SectorGroup
        fields = "__all__"


class ParticipantTypeSerializer(serializers.ModelSerializer):
    actors_count = serializers.ReadOnlyField()

    class Meta:
        model = ParticipantType
        fields = "__all__"


class ParticipantGroupSerializer(serializers.ModelSerializer):
    participant_types_count = serializers.ReadOnlyField()

    class Meta:
        model = ParticipantGroup
        fields = "__all__"


class ParticipantGroupFullSerializer(serializers.ModelSerializer):
    participant_types = ParticipantTypeSerializer(
        many=True, read_only=True)

    class Meta:
        model = ParticipantGroup
        fields = "__all__"


class BelongSerializer(serializers.ModelSerializer):
    actors_count = serializers.ReadOnlyField()

    class Meta:
        model = Belong
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    actors_count = serializers.ReadOnlyField()

    class Meta:
        model = Country
        fields = "__all__"
