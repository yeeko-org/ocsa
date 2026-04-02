from rest_framework import viewsets
from django_filters import FilterSet, NumberFilter
from django.db.models import Count
from api.permissions import IsAdminOrReadOnly, IsEditorOrCreateOrRead
# from rest_framework.decorators import action
# from rest_framework.response import Response

from work_flux.models import StatusControl

from project.models import MegaprojectType, StatusProject

from api.views.catalogs.serializers import StatusControlSerializer
from api.views.catalogs.project_serializers import (
    MegaprojectTypeCountSerializer,
    MegaprojectTypeFullSerializer,
    StatusProjectFullSerializer,
)
from .all import CatalogsView  # noqa
from ..common_views import BaseStatusViewSet, ClickHistoryMixin


class StatusControlViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = StatusControl.objects.all()
    serializer_class = StatusControlSerializer


class StatusProjectViewSet(ClickHistoryMixin, BaseStatusViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    is_mention_child = True
    queryset = StatusProject.objects.all()\
        .annotate(projects_count=Count('projects'))\
        .distinct()
    serializer_class = StatusProjectFullSerializer


class MegaprojectTypeFilter(FilterSet):
    permission_classes = [IsEditorOrCreateOrRead]
    extractivism_type = NumberFilter(
        field_name='extractivism_types', lookup_expr='exact')

    class Meta:
        model = MegaprojectType
        fields = {'status_validation': ['exact']}


class MegaprojectTypeViewSet(BaseStatusViewSet):
    permission_classes = [IsEditorOrCreateOrRead]

    queryset = MegaprojectType.objects.all()\
        .annotate(count=Count('projects'))\
        .prefetch_related('extractivism_types', 'projects', 'status_validation')\
        .distinct()

    filterset_class = MegaprojectTypeFilter
    serializer_class = MegaprojectTypeCountSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': MegaprojectTypeFullSerializer,
            'create': MegaprojectTypeCountSerializer,
            'update': MegaprojectTypeCountSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
