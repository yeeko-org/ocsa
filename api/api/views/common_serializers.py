from rest_framework import serializers
from space_time.models import Location, State, Municipality, Locality


class CommonCount(serializers.ModelSerializer):
    count = serializers.ReadOnlyField()


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ['id', 'name', 'inegi_code']


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ['id', 'name', 'inegi_code']



class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = ['id', 'name', 'inegi_code']


class LocationExportSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    municipality = MunicipalitySerializer()
    locality = LocalitySerializer()

    class Meta:
        model = Location
        fields = '__all__'


class BaseExportSerializer(serializers.ModelSerializer):
    location_id = serializers.ReadOnlyField()
    state__inegi_code = serializers.ReadOnlyField()
    state__short_name = serializers.ReadOnlyField()
    municipality__inegi_code = serializers.ReadOnlyField()
    municipality__name = serializers.ReadOnlyField()
    locality__inegi_code = serializers.ReadOnlyField()
    locality__name = serializers.ReadOnlyField()
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()
