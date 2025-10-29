from rest_framework import viewsets, permissions
from django_filters import FilterSet, CharFilter

from api.pagination import CustomPagination
from api.permissions import LocationPermission
from rest_framework.response import Response
from space_time.models import (
    State,
    Municipality,
    Locality,
    Location,)

from api.views.space_time.serializers import (
    MunicipalityRetrieveSerializer,
    StateListSerializer,
    MunicipalityListSerializer,
    LocalitySerializer,
    LocationSerializer,
    LocationSemiFullSerializer,
    LocationFullSerializer,
    StateRetrieveSerializer,)
from ..common_views import (
    BaseViewSet, BaseStatusViewSet, OnlyByFilterMixin, BaseGenericViewSet)



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


class LocalityListViewSet(ListSetMixin):
    queryset = Locality.objects.all()
    serializer_class = LocalitySerializer


class LocationFilter(OnlyByFilterMixin):

    class Meta:
        model = Location
        fields = ['only_by', "status_location", "state", "type_location"]


class LocationViewSet(BaseViewSet):
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if 'project' in request.data:
            serializer.instance.project.editors.add(request.user)
        final_serializer = self.get_serializer(serializer.instance)
        return Response(final_serializer.data)

    def get_serializer_class(self):
        # action_serializer = {'list': LocationSerializer}
        action_serializer = {'list': LocationSemiFullSerializer}
        return action_serializer.get(self.action, self.serializer_class)

