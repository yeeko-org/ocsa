from rest_framework import serializers
from event.models import Event, Involved, EventType

from api.views.actor.serializers import MentionBaseSerializer
from api.views.common_serializers import (
    ConditionalFieldsMixin, ParticipantFullSerializer)
from project.models import Conflict
from space_time.models import Location
from df.models import Displacement


class InvolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Involved
        fields = '__all__'


class InvolvedFullSerializer(InvolvedSerializer):
    participant_full = ParticipantFullSerializer(
        read_only=True, source='participant')
    example = serializers.SerializerMethodField(read_only=True)

    def get_example(self, obj):
        return "SOLO"

    class Meta:
        model = Involved
        fields = '__all__'


class LocationSimpleSerializer(ConditionalFieldsMixin):
    class Meta:
        model = Location
        fields = '__all__'


class DisplacementSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = '__all__'


class EventMediumSerializer(serializers.ModelSerializer):
    involvements = InvolvedSerializer(many=True, read_only=True)
    locations = LocationSimpleSerializer(many=True, read_only=True)
    displacements = DisplacementSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class EventSerializer(EventMediumSerializer):
    involvements = InvolvedFullSerializer(many=True, read_only=True)
    mention_full = MentionBaseSerializer(read_only=True, source='mention')


class ConflictSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conflict
        fields = '__all__'
