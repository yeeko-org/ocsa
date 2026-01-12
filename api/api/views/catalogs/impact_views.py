from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, NumberFilter
from api.pagination import CustomPagination
from api.views.common_views import UnaccentSearchFilter, OrderingAutoFilter
from api.permissions import IsAdminOrReadOnly, IsEditorOrCreateOrRead
from api.views.catalogs.serializers import (
    ImpactSubtypeSerializer, ImpactSubtypeFullSerializer,
    ImpactTypeSerializer, ImpactTypeFullSerializer,
    ImpactGroupSerializer)
from impact.models import ImpactSubtype, ImpactType, ImpactGroup


class ImpactGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = ImpactGroup.objects.all()
    serializer_class = ImpactGroupSerializer


class ImpactTypeFilter(FilterSet):

    class Meta:
        model = ImpactType
        fields = {
            'impact_group': ['exact'],
            'status_validation': ['exact']
        }


class ImpactTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    from django.db.models import Count

    queryset = ImpactType.objects.all()\
        .annotate(impact_subtype_count=Count('impact_subtypes'),
                  mentions_count=Count('impact'))\
        .distinct()
    filterset_class = ImpactTypeFilter
    pagination_class = CustomPagination
    filter_backends = [
        UnaccentSearchFilter, DjangoFilterBackend, OrderingAutoFilter]
    search_fields = ['name']
    ordering_fields = ['__auto__']

    serializer_class = ImpactTypeFullSerializer

    def get_serializer_class(self):
        action_serializer = {
            'list': ImpactTypeSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class ImpactSubtypeFilter(FilterSet):

    class Meta:
        model = ImpactSubtype
        fields = {
            'impact_type': ['exact'],
            'status_validation': ['exact']
        }


class ImpactSubtypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    from django.db.models import Count
    queryset = ImpactSubtype.objects.all()\
        .annotate(mentions_count=Count('impact'))\
        .distinct()

    # filterset_class = ImpactSubtypeFilter
    filterset_fields = ['impact_type', 'status_validation']
    pagination_class = CustomPagination
    filter_backends = [
        UnaccentSearchFilter, DjangoFilterBackend, OrderingAutoFilter]
    search_fields = ['name']
    ordering_fields = ['__auto__']

    serializer_class = ImpactSubtypeFullSerializer

    def get_serializer_class(self):
        action_serializer = {
            'list': ImpactSubtypeSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
