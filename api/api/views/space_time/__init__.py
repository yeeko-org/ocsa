from rest_framework import viewsets, permissions

from api.pagination import CustomPagination
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
    StateRetrieveSerializer,)


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


class LocationListViewSet(ListSetMixin):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
