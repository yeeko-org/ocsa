from rest_framework import serializers
from event.models import (
    EventGroup,
    EventType,
    EventSubtype,
    InvolvedRole,)


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
    # event_types = EventTypeSerializer(many=True)
    # status_validation = StatusControlSerializer()

    class Meta:
        model = EventSubtype
        fields = "__all__"


class InvolvedRoleSerializer(serializers.ModelSerializer):
    # event_group = serializers.ReadOnlyField()

    class Meta:
        model = InvolvedRole
        fields = "__all__"

