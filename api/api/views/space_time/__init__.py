import tempfile
from pathlib import Path

from rest_framework import viewsets, permissions
from django_filters import BooleanFilter, CharFilter

from api.pagination import CustomPagination
from api.permissions import LocationPermission
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from space_time.completeness import completeness_q
from space_time.geo_import import GeoImportError, read_geo_file
from space_time.geometry import (
    has_geometry_q, infer_type_location, normalize_location_geometry)
from space_time.models import (
    State,
    Municipality,
    Location,)

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
    BaseViewSet, OnlyByFilterMixin, ClickHistoryMixin)



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
    completeness = CharFilter(method='filter_completeness')

    def filter_completeness(self, queryset, name, value):
        condition = completeness_q(value) if value else None
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


class LocationViewSet(ClickHistoryMixin, BaseViewSet):
    permission_classes = [LocationPermission]
    queryset = Location.objects.all().exclude(
        project__isnull=True, event__isnull=True, impact__isnull=True)\
        .select_related("event", "impact", "project")
    serializer_class = LocationFullSerializer
    search_fields = ['state__name',
                     'municipality__name',
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

