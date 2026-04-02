from rest_framework import serializers
from df.models import Displacement
from api.views.event import EventSerializer
from api.views.project.list_serializers import ImpactSerializer


class DisplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = "__all__"


class DisplacementFullSerializer(DisplacementSerializer):
    event_full = EventSerializer(read_only=True, source='event')
    impact_full = ImpactSerializer(read_only=True, source='impact')


class DisplacementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = "__all__"
