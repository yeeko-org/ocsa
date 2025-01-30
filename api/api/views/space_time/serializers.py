from rest_framework import serializers

from space_time.models import (
    State,
    Municipality,
    Locality,
    Location,)
from api.views.event import EventSerializer
from api.views.project import ProjectBasicSerializer
from api.views.project.list_serializers import ImpactSerializer


class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = '__all__'


class MunicipalityListSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(
        view_name='space_time_municipality-detail',
        lookup_field='pk'
    )

    class Meta:
        model = Municipality
        fields = '__all__'


class MunicipalityRetrieveSerializer(MunicipalityListSerializer):
    localities = LocalitySerializer(many=True, read_only=True)

    class Meta:
        model = Municipality
        fields = '__all__'


class StateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class StateRetrieveSerializer(StateListSerializer):
    municipalities = MunicipalityListSerializer(many=True, read_only=True)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class LocationFullSerializer(serializers.ModelSerializer):
    event_full = EventSerializer(read_only=True, source='event')
    project_full = ProjectBasicSerializer(read_only=True, source='project')
    impact_full = ImpactSerializer(read_only=True, source='impact')

    class Meta:
        model = Location
        fields = '__all__'
