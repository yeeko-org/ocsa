from rest_framework import viewsets, permissions
from django_filters import FilterSet, CharFilter

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
from ..common_views import BaseViewSet, BaseStatusViewSet


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


class LocationFilter(FilterSet):

    only_by = CharFilter(method='filter_only_by')

    def filter_only_by(self, queryset, name, value):
        options = ["project", "event", "impact"]
        if value not in options:
            return queryset

        filter_kwargs = {f"{value}__isnull": False}
        return queryset.filter(**filter_kwargs)

    class Meta:
        model = Location
        fields = ['only_by', "status_location"]


class LocationViewSet(BaseViewSet):
    queryset = Location.objects.all().exclude(
        project__isnull=True, event__isnull=True, impact__isnull=True)
    serializer_class = LocationSerializer

    filterset_class = LocationFilter
