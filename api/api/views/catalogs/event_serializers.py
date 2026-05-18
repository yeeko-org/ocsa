from rest_framework import serializers
from event.models import (
    EventGroup, EventType, InvolvedRole, Purpose)

from api.views.common_serializers import CommonCount


class EventGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGroup
        fields = "__all__"


class EventTypeFullSerializer(serializers.ModelSerializer):
    events_count = serializers.SerializerMethodField()

    def get_events_count(self, obj: EventType):
        return obj.events.count()

    class Meta:
        model = EventType
        fields = "__all__"


class EventTypeSerializer(CommonCount):

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


