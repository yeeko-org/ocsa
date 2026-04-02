from api.views.actor import ActorBaseSerializer
from api.views.common_serializers import CommonCount
from classify.models import IndigenousGroup, ParticipantGroup, ParticipantType
from rest_framework import serializers


class IndigenousGroupFullSerializer(CommonCount):
    actors = ActorBaseSerializer(many=True, read_only=True)

    class Meta:
        model = IndigenousGroup
        fields = "__all__"


class ParticipantTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipantType
        fields = "__all__"


class ParticipantGroupFullSerializer(serializers.ModelSerializer):
    participant_types = ParticipantTypeSerializer(many=True, read_only=True)

    class Meta:
        model = ParticipantGroup
        fields = "__all__"