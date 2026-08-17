from rest_framework import viewsets, permissions
from django_filters import BooleanFilter, CharFilter

from api.pagination import CustomPagination
from api.permissions import LocationPermission
from rest_framework.response import Response
from space_time.completeness import completeness_q
from space_time.geometry import has_geometry_q
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
        }
        return action_serializer.get(self.action, self.serializer_class)
