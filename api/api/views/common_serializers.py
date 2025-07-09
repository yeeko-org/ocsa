from rest_framework import serializers
from space_time.models import Location, State, Municipality, Locality


class CommonCount(serializers.ModelSerializer):
    count = serializers.ReadOnlyField()


class ConditionalFieldsMixin(serializers.ModelSerializer):
    """
    A serializer mixin that conditionally excludes fields based on
    user authentication.
    """

    def to_representation(self, instance):
        """
        Override to_representation to handle conditional fields.
        """
        data = super().to_representation(instance)
        context = self.context
        protected_fields = [
            'status_register', 'comments', 'status_validation',
            'status_location']

        # Remove protected fields from the nested serializer
        is_authenticated = context.get('request', {}).user.is_authenticated
        if not is_authenticated:
            for field in protected_fields:
                if field in data:
                    data.pop(field)
        return data


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
