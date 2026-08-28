from rest_framework import serializers

from api.views.common_serializers import MunicipalitySimpleSerializer
from space_time.geolocate import apply_geolocation
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
# Derivados de la geometría por el servidor: el editor los muestra, pero
# nunca los manda.
DERIVED_FIELDS = ["municipalities"]


class LocationGeometryMixin(serializers.ModelSerializer):
    """Aplica el contrato de `Location.geojson` en todo camino de escritura.

    Ver `space_time.geometry`. La geometría no se valida cuando la
    escritura no toca ninguno de sus campos (patch parcial, edición
    masiva): así una fila heredada inconsistente sigue siendo editable en
    lo demás mientras el comando de rescate no la corrige.
    """

    municipalities_full = MunicipalitySimpleSerializer(
        many=True, read_only=True, source="municipalities")

    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = DERIVED_FIELDS

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        if not any(field in attrs for field in GEOMETRY_FIELDS):
            return attrs

        def current(field: str):
            if field in attrs:
                return attrs[field]
            return getattr(self.instance, field, None)

        type_location = current("type_location") or "point"
        # En un trazo el par lat/lon es el centroide, y su dueño es el
        # servidor: lo que mande el cliente se descarta.
        latitude, longitude = (
            (None, None) if type_location != "point"
            else (current("latitude"), current("longitude")))
        try:
            geojson, latitude, longitude = normalize_location_geometry(
                current("geojson"), type_location, latitude, longitude)
        except ValueError as error:
            raise serializers.ValidationError({"geojson": str(error)})
        attrs["geojson"] = geojson
        attrs["latitude"] = latitude
        attrs["longitude"] = longitude
        return attrs

    def create(self, validated_data: dict):
        instance = super().create(validated_data)
        self._geolocate(instance, validated_data, created=True)
        return instance

    def update(self, instance, validated_data: dict):
        instance = super().update(instance, validated_data)
        self._geolocate(instance, validated_data, created=False)
        return instance

    @staticmethod
    def _geolocate(instance, validated_data: dict, created: bool) -> None:
        """Recalcula solo cuando la escritura tocó la geometría.

        Una escritura ajena a la geometría no puede cambiar lo derivado,
        y un hueco en `state`/`municipality`/`locality` puede ser
        deliberado: reintentarlo en cada guardado lo volvería a llenar.
        """
        touched_geometry = created or any(
            field in validated_data for field in GEOMETRY_FIELDS)
        if not touched_geometry:
            return
        filled = apply_geolocation(instance, geometry_changed=True)
        if filled:
            instance.save()


class LocationSerializer(LocationGeometryMixin):
    class Meta(LocationGeometryMixin.Meta):
        pass


class LocationSemiFullSerializer(LocationGeometryMixin):
    # event_full = EventSerializer(read_only=True, source='event')
    project_full = ProjectMiniSerializer(read_only=True, source='project')
    # impact_full = ImpactSerializer(read_only=True, source='impact')

    class Meta(LocationGeometryMixin.Meta):
        pass


class LocationFullSerializer(LocationGeometryMixin):
    event_full = EventSerializer(read_only=True, source='event')
    project_full = ProjectBasicSerializer(read_only=True, source='project')
    impact_full = ImpactSerializer(read_only=True, source='impact')

    class Meta(LocationGeometryMixin.Meta):
        pass


class GeoImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    type_location = serializers.ChoiceField(
        choices=TYPE_LOCATIONS, required=False)
    layer = serializers.CharField(required=False, allow_blank=True)
