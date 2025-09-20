from rest_framework import serializers
from event.models import Event, Involved, EventType, EventSubtype, EventGroup

from api.views.actor.serializers import MentionBaseSerializer
from api.views.common_serializers import BaseExportSerializer
from project.models import Conflict
from impact.models import ImpactType, Impact


class InvolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Involved
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    involvements = InvolvedSerializer(many=True, read_only=True)
    mention_full = MentionBaseSerializer(read_only=True, source='mention')

    class Meta:
        model = Event
        fields = '__all__'


class EventFullSerializer(serializers.ModelSerializer):
    involvements = InvolvedSerializer(many=True)
    mention = MentionBaseSerializer()

    class Meta:
        model = Event
        fields = '__all__'


class EventTypeSerializer(serializers.ModelSerializer):
    event_group  = serializers.CharField(
        source='event_group.name', read_only=True)

    class Meta:
        model = EventType
        fields = '__all__'


class ImpactTypeSerializer(serializers.ModelSerializer):
    impact_group  = serializers.CharField(
        source='impact_group.name', read_only=True)

    class Meta:
        model = ImpactType
        fields = "__all__"


class ConflictSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conflict
        fields = '__all__'


class EventExportSerializer(BaseExportSerializer):
    mention = MentionBaseSerializer()

    conflict = ConflictSimpleSerializer(
        source='mention.project.conflict', read_only=True)
    event_type = EventTypeSerializer()
    event_subtype = serializers.CharField(
        source='event_subtype.name', read_only=True)
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
            'event_subtype',
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


class ImpactExportSerializer(BaseExportSerializer):
    mention = MentionBaseSerializer()

    conflict = ConflictSimpleSerializer(
        source='mention.project.conflict', read_only=True)
    impact_type = ImpactTypeSerializer()
    impact_subtype = serializers.CharField(
        source='impact_subtype.name', read_only=True)

    class Meta:
        model = Impact
        fields = [
            'id',
            'description',
            'impact_type',
            'impact_subtype',

            'mention',
            'conflict',

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
