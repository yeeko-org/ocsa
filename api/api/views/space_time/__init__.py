import tempfile
from pathlib import Path

from rest_framework import viewsets, permissions
from django_filters import BooleanFilter, CharFilter

from api.pagination import CustomPagination
from api.permissions import LocationPermission
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from space_time.completeness import location_pending_q
from space_time.geo_import import GeoImportError, read_geo_file
from space_time.geolocate import (
    LOCALITY_TOLERANCE_M, feature_to_shape, localities_within,
    resolve_geometry, resolve_point)
from space_time.geometry import (
    has_geometry_q, infer_type_location, normalize_location_geometry)
from space_time.models import (
    State,
    Municipality,
    Location,)

from api.views.common_serializers import (
    LocalitySimpleSerializer, MunicipalitySimpleSerializer)
from api.views.space_time.serializers import (
    MunicipalityRetrieveSerializer,
    StateListSerializer,
    StateReportSerializer,
    MunicipalityListSerializer,
    LocalitySerializer,
    LocationSerializer,
    LocationSemiFullSerializer,
    LocationFullSerializer,
    GeoImportSerializer,
    StateRetrieveSerializer,)
from api.views.common_views import (
    BaseViewSet, OnlyByFilterMixin, ClickHistoryMixin, MassiveEdit)



class ListSetMixin(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


class StateListViewSet(ListSetMixin):
    queryset = State.objects.all().prefetch_related('municipalities')
    serializer_class = StateListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StateRetrieveSerializer
        return self.serializer_class


class MunicipalityListViewSet(ListSetMixin):
    queryset = Municipality.objects.all().prefetch_related('localities')
    serializer_class = MunicipalityListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MunicipalityRetrieveSerializer
        return self.serializer_class


class LocationFilter(OnlyByFilterMixin):

    has_geo_data = BooleanFilter(method='filter_has_geo_data')
    pending = CharFilter(method='filter_pending')

    def filter_pending(self, queryset, name, value):
        condition = location_pending_q(value) if value else None
        if condition is None:
            return queryset
        return queryset.filter(condition)

    def filter_has_geo_data(self, queryset, name, value):
        has_geo = has_geometry_q()
        if value:
            return queryset.filter(has_geo)
        return queryset.exclude(has_geo)

    class Meta:
        model = Location
        fields = ['only_by', "status_location", "state", "type_location"]


class LocationViewSet(ClickHistoryMixin, MassiveEdit, BaseViewSet):
    permission_classes = [LocationPermission]
    queryset = Location.objects.all().exclude(
        project__isnull=True, event__isnull=True, impact__isnull=True)\
        .select_related("event", "impact", "project")\
        .prefetch_related("municipalities")
    serializer_class = LocationFullSerializer
    search_fields = ['state__name',
                     'municipality__name',
                     'municipalities__name',
                     'locality__name',
                     'details', 'comments']
    # filter_backends = [OrderingFilter, DjangoFilterBackend, SearchFilter]
    ordering_fields = ['id', 'status_location__order']
    filterset_class = LocationFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        location = serializer.instance
        if location.project:
            location.project.editors.add(request.user)
            self.save_click_action(request, location, 'created', force=True)
        final_serializer = self.get_serializer(serializer.instance)
        return Response(final_serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if serializer.instance.project:
            serializer.instance.project.editors.add(request.user)
            self.save_click_action(request, instance, 'updated', force=True)
        final_serializer = self.get_serializer(serializer.instance)
        return Response(final_serializer.data)

    def get_serializer_class(self):
        # action_serializer = {'list': LocationSerializer}
        action_serializer = {
            'list': LocationSemiFullSerializer,
            'import_geo': GeoImportSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    @action(detail=False, methods=['get', 'post'], url_path='geolocate',
            permission_classes=[permissions.IsAuthenticated])
    def geolocate(self, request):
        """Sugiere entidad, municipio y localidad antes de guardar.

        Ruta de lista y no de detalle porque el editor la consulta
        mientras dibuja, sobre una ubicación que puede no existir aún:
        no toca la base.

        GET, para un punto: `lat`, `lon` y el `state` ya capturado —si
        el punto cae dentro, se respeta y se ahorra la búsqueda por
        polígono—.

        POST, para un trazo: `{"geojson": <Feature o geometría>,
        "state": <id|null>}`. Devuelve además los municipios que el
        trazo atraviesa, en el orden del motor (de mayor a menor
        medida), las localidades a `LOCALITY_TOLERANCE_M` o menos del
        trazo y el centroide con el que se pinta el pin.
        """
        if request.method == 'POST':
            return self._geolocate_geometry(request)
        try:
            latitude = float(request.query_params["lat"])
            longitude = float(request.query_params["lon"])
        except (KeyError, TypeError, ValueError):
            return Response(
                {'detail': 'Faltan las coordenadas o no son números: '
                           'se esperan «lat» y «lon» en grados decimales.'},
                status=400)
        state = request.query_params.get('state') or None
        try:
            state_id = int(state) if state else None
        except (TypeError, ValueError):
            state_id = None
        resolution = resolve_point(latitude, longitude, state_id)
        return Response({
            'state': _named(resolution.state),
            'municipality': _named(resolution.municipality),
            'locality': _named(resolution.locality),
        })

    @staticmethod
    def _geolocate_geometry(request):
        feature = request.data.get('geojson')
        if not isinstance(feature, dict) or not feature:
            return Response(
                {'detail': 'Falta el trazo o no es un objeto GeoJSON: se '
                           'espera «geojson» con un Feature o una '
                           'geometría.'},
                status=400)
        try:
            state = request.data.get('state') or None
            state_id = int(state) if state else None
        except (TypeError, ValueError):
            state_id = None
        # `feature_to_shape` solo desenvuelve Features: una geometría
        # pelona trae su propio «type» y lo haría buscar un «geometry»
        # que no existe.
        if feature.get('type') != 'Feature' and 'coordinates' in feature:
            feature = {'type': 'Feature', 'geometry': feature}
        try:
            resolution = resolve_geometry(feature, state_id)
        except (AttributeError, KeyError, TypeError, ValueError):
            return Response(
                {'detail': 'No se pudo leer el trazo: revisa que el '
                           'GeoJSON tenga coordenadas válidas.'},
                status=400)
        municipalities = [
            municipality for municipality, _ in resolution.municipalities]
        centroid = resolution.centroid
        # La lista del aviso no es la del autollenado: aquí se toleran
        # 5 km y allá se exige contacto a 500 m (docs `adr-0026`), así
        # que se recalcula con la tolerancia del editor.
        nearby = localities_within(
            feature_to_shape(feature), municipalities, LOCALITY_TOLERANCE_M)
        return Response({
            'state': _named(_geometry_state(
                resolution.single_municipality, municipalities)),
            # adr-0026: el municipio base es único; el motor no elige
            # entre varios atravesados.
            'municipality': _named(resolution.single_municipality),
            'locality': _named(resolution.locality),
            'municipalities': MunicipalitySimpleSerializer(
                municipalities, many=True).data,
            # Todas las que quedan cerca, no solo la única: el editor
            # avisa con ellas cuando la localidad capturada queda lejos.
            'localities': LocalitySimpleSerializer(nearby, many=True).data,
            'centroid': None if not centroid else {
                'latitude': centroid[0], 'longitude': centroid[1]},
        })

    @action(detail=False, methods=['post'], url_path='import_geo',
            parser_classes=[MultiPartParser, FormParser],
            permission_classes=[permissions.IsAuthenticated])
    def import_geo(self, request):
        """Lee un archivo geográfico y devuelve la geometría normalizada.

        Ruta de lista y no de detalle porque el editor importa también
        sobre una ubicación todavía no guardada: no toca la base, el
        front aplica el resultado al formulario y guarda cuando quiere.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data["file"]
        layer = serializer.validated_data.get("layer") or None
        try:
            collection = self._read_upload(upload, layer)
        except GeoImportError as error:
            return Response({'detail': str(error)}, status=400)
        type_location = (
            serializer.validated_data.get("type_location")
            or infer_type_location(collection) or "point")
        try:
            geojson, latitude, longitude = normalize_location_geometry(
                collection, type_location)
        except ValueError as error:
            return Response({'detail': str(error)}, status=400)
        # El punto no guarda geojson: su parte es el par de coordenadas.
        parts = _count_parts(geojson) or (1 if latitude is not None else 0)
        return Response({
            'geojson': geojson,
            'type_location': type_location,
            'parts': parts,
            'latitude': latitude,
            'longitude': longitude,
            'warnings': _import_warnings(collection, parts),
        })

    @staticmethod
    def _read_upload(upload, layer: str | None) -> dict:
        """GDAL necesita una ruta en disco: el archivo no se conserva."""
        suffix = Path(upload.name).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=suffix) as temporary:
            for chunk in upload.chunks():
                temporary.write(chunk)
            temporary.flush()
            return read_geo_file(temporary.name, upload.name, layer)


def _geometry_state(single_municipality, municipalities: list):
    """Estado de un trazo: el del municipio base, o el que comparten.

    Un trazo puede cruzar la frontera estatal; sugerir un estado cuando
    los atravesados no coinciden sería elegir por el capturista.
    """
    if single_municipality is not None:
        return single_municipality.state
    states = {municipality.state_id for municipality in municipalities}
    if len(states) == 1:
        return municipalities[0].state
    return None


def _named(instance) -> dict | None:
    if instance is None:
        return None
    return {'id': instance.pk, 'name': instance.name}


def _count_parts(geojson: dict | None) -> int:
    if not geojson:
        return 0
    geometry = geojson.get("geometry") or {}
    kind = geometry.get("type") or ""
    if kind.startswith("Multi"):
        return len(geometry.get("coordinates") or [])
    return 1 if kind else 0


def _import_warnings(collection: dict, parts: int) -> list[str]:
    source = collection.get("properties") or {}
    warnings = []
    if source.get("reprojected"):
        warnings.append(
            f"Se reproyectó de {source.get('source_crs')} a EPSG:4326.")
    read_count = source.get("geometries_read") or 0
    if read_count > parts:
        warnings.append(
            f"Se descartaron {read_count - parts} geometrías vacías, "
            "degeneradas o de otro tipo.")
    return warnings

