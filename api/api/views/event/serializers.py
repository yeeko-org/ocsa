from rest_framework import serializers
from event.models import Event, Involved, EventType

from api.views.actor.serializers import MentionBaseSerializer
from api.views.common_serializers import (
    LocationBaseExportSerializer, ConditionalFieldsMixin, ParticipantFullSerializer)
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


class EventTypeSerializer(serializers.ModelSerializer):
    event_group  = serializers.CharField(
        source='event_group.name', read_only=True)

    class Meta:
        model = EventType
        fields = '__all__'


class ConflictSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conflict
        fields = '__all__'


class EventExportSerializer(serializers.ModelSerializer):
    event_type = EventTypeSerializer()
    purpose = serializers.CharField(
        source='purpose.name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'date',
            'description',
            'number_women',
            'number_men',
            'number_mix',
            'event_type',
            'purpose',
        ]
        read_only_fields = fields


class EventExportFullSerializer(
    EventExportSerializer, LocationBaseExportSerializer):
    mention = MentionBaseSerializer()
    conflict = ConflictSimpleSerializer(
        source='mention.project.conflict', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'date',
            'description',
            'number_women',
            'number_men',
            'number_mix',
            'event_type',
            'purpose',

            'conflict',
            'mention',

            "location_id",
            "state__inegi_code",
            "state__short_name",
            "municipality__inegi_code",
            "municipality__name",
            "locality__inegi_code",
            "locality__name",
            "latitude",
            "longitude",
        ]
        read_only_fields = fields


