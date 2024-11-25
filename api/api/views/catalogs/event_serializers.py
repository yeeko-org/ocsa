from rest_framework import serializers
from event.models import (
    EventGroup,
    EventType,
    EventSubtype,
    InvolvedRole,)
from api.views.event.serializers import EventSerializer


class EventGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGroup
        fields = "__all__"


class EventTypeSerializer(serializers.ModelSerializer):
    # group = EventGroupSerializer()
    # status_validation = StatusControlSerializer()

    class Meta:
        model = EventType
        fields = "__all__"


class EventSubtypeSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = EventSubtype
        fields = "__all__"


class EventSubtypeFullSerializer(EventSubtypeSerializer):
    events = EventSerializer(many=True, read_only=True)


class InvolvedRoleSerializer(serializers.ModelSerializer):
    # event_group = serializers.ReadOnlyField()

    class Meta:
        model = InvolvedRole
        fields = "__all__"

