from rest_framework import serializers
from event.models import (
    EventGroup,
    EventType,
    EventSubtype,
    InvolvedRole,
    Purpose)
from api.views.event.serializers import EventSerializer
from api.views.common_serializers import CommonCount


class EventGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGroup
        fields = "__all__"


class EventSubtypeSerializer(CommonCount):

    class Meta:
        model = EventSubtype
        fields = "__all__"


class EventSubtypeFullSerializer(EventSubtypeSerializer):
    events_count = serializers.SerializerMethodField()

    def get_events_count(self, obj: EventType):
        return obj.events.count()


class EventTypeFullSerializer(serializers.ModelSerializer):
    events_count = serializers.SerializerMethodField()
    event_subtypes = EventSubtypeSerializer(many=True, read_only=True)

    def get_events_count(self, obj: EventType):
        return obj.events.count()

    class Meta:
        model = EventType
        fields = "__all__"


class EventTypeSerializer(CommonCount):
    # impact_subtype_count = serializers.IntegerField(read_only=True)
    # event_subtype_count = serializers.IntegerField(read_only=True)
    event_subtype_count = serializers.SerializerMethodField()

    def get_event_subtype_count(self, obj):
        return obj.event_subtypes.count()

    class Meta:
        model = EventType
        fields = "__all__"


class InvolvedRoleSerializer(serializers.ModelSerializer):
    # event_group = serializers.ReadOnlyField()

    class Meta:
        model = InvolvedRole
        fields = "__all__"


class PurposeSerializer(serializers.ModelSerializer):
    events_count = serializers.ReadOnlyField()

    class Meta:
        model = Purpose
        fields = "__all__"


