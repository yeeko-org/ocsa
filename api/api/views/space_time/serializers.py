from rest_framework import serializers

from space_time.geometry import normalize_location_geometry
from space_time.models import (
    State,
    Municipality,
    Locality,
    Location,
    TYPE_LOCATIONS,)
from api.views.event import EventSerializer
from api.views.project import ProjectBasicSerializer
from api.views.project.list_serializers import ProjectMiniSerializer
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


class StateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class StateRetrieveSerializer(StateListSerializer):
    municipalities = MunicipalityListSerializer(many=True, read_only=True)


GEOMETRY_FIELDS = ["geojson", "type_location", "latitude", "longitude"]


class LocationGeometryMixin(serializers.ModelSerializer):
    """Aplica el contrato de `Location.geojson` en todo camino de escritura.

    Ver `space_time.geometry`. La geometría no se valida cuando la
    escritura no toca ninguno de sus campos (patch parcial, edición
    masiva): así una fila heredada inconsistente sigue siendo editable en
    lo demás mientras el comando de rescate no la corrige.
    """

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        if not any(field in attrs for field in GEOMETRY_FIELDS):
            return attrs

        def current(field: str):
            if field in attrs:
                return attrs[field]
            return getattr(self.instance, field, None)

        type_location = current("type_location") or "point"
        try:
            geojson, latitude, longitude = normalize_location_geometry(
                current("geojson"), type_location,
                current("latitude"), current("longitude"))
        except ValueError as error:
            raise serializers.ValidationError({"geojson": str(error)})
        attrs["geojson"] = geojson
        attrs["latitude"] = latitude
        attrs["longitude"] = longitude
        return attrs


class LocationSerializer(LocationGeometryMixin):
    class Meta:
        model = Location
        fields = '__all__'


class LocationSemiFullSerializer(LocationGeometryMixin):
    # event_full = EventSerializer(read_only=True, source='event')
    project_full = ProjectMiniSerializer(read_only=True, source='project')
    # impact_full = ImpactSerializer(read_only=True, source='impact')

    class Meta:
        model = Location
        fields = '__all__'


class LocationFullSerializer(LocationGeometryMixin):
    event_full = EventSerializer(read_only=True, source='event')
    project_full = ProjectBasicSerializer(read_only=True, source='project')
    impact_full = ImpactSerializer(read_only=True, source='impact')

    class Meta:
        model = Location
        fields = '__all__'


class GeoImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    type_location = serializers.ChoiceField(
        choices=TYPE_LOCATIONS, required=False)
    layer = serializers.CharField(required=False, allow_blank=True)
