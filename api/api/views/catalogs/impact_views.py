from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, NumberFilter
from api.pagination import CustomPagination
from impact.models import ImpactSubtype, ImpactType
from api.views.catalogs.serializers import (
    ImpactSubtypeSerializer, ImpactTypeSerializer)
from ..common_views import BaseViewSet, BaseStatusViewSet


class ImpactSubtypeFilter(FilterSet):

    class Meta:
        model = ImpactSubtype
        fields = {
            'impact_type': ['exact'],
            'status_validation': ['exact']
        }


class ImpactSubtypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    # from django.db.models import Count

    permission_classes = [permissions.AllowAny]
    filterset_class = ImpactSubtypeFilter
    queryset = ImpactSubtype.objects.all()
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    serializer_class = ImpactSubtypeSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ImpactSubtypeSerializer,
            'create': ImpactSubtypeSerializer,
            'update': ImpactSubtypeSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)


class ImpactTypeFilter(FilterSet):

    class Meta:
        model = ImpactType
        fields = {
            'impact_group': ['exact'],
            'status_validation': ['exact']
        }


class ImpactTypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = ImpactType.objects.all()
    permission_classes = [permissions.AllowAny]
    filterset_class = ImpactTypeFilter
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    serializer_class = ImpactTypeSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ImpactTypeSerializer,
            'create': ImpactTypeSerializer,
            'update': ImpactTypeSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
