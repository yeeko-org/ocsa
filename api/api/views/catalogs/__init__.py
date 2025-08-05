from rest_framework import viewsets
from django_filters import FilterSet, NumberFilter
from django.db.models import Count
from api.permissions import IsAdminOrReadOnly, IsEditorOrCreateOrRead
# from rest_framework.decorators import action
# from rest_framework.response import Response

from classify.models import (
    InterestGroup,
    InterestType,
    InterestSubtype, )
from event.models import (
    InvolvedRole,)

from work_flux.models import StatusControl

from project.models import MegaprojectType, ExtractivismType, StatusProject

from api.views.catalogs.event_serializers import InvolvedRoleSerializer

from api.views.catalogs.classify_serializers import (
    InterestGroupSerializer, InterestTypeSerializer,
    InterestSubtypeSerializer
)
from api.views.catalogs.serializers import (
    SourceSerializer, StatusControlSerializer,
)
from api.views.catalogs.project_serializers import (
    ExtractivismTypeSerializer,
    MegaprojectTypeCountSerializer,
    MegaprojectTypeFullSerializer,
    StatusProjectSerializer,
    StatusProjectFullSerializer,
)
from .all import CatalogsView  # noqa
from ..common_views import BaseViewSet, BaseStatusViewSet
from api.views.confirm_delete import CustomDeleteMixin


class InterestGroupViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = InterestGroup.objects.all()
    serializer_class = InterestGroupSerializer


class InterestTypeViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    queryset = InterestType.objects.all()
    serializer_class = InterestTypeSerializer


class InterestSubtypeViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    queryset = InterestSubtype.objects.all()
    serializer_class = InterestSubtypeSerializer


class InvolvedRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    queryset = InvolvedRole.objects.all()
    serializer_class = InvolvedRoleSerializer


class StatusControlViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = StatusControl.objects.all()
    serializer_class = StatusControlSerializer


class StatusProjectViewSet(BaseStatusViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    queryset = StatusProject.objects.all()\
        .annotate(projects_count=Count('projects'))\
        .distinct()
    serializer_class = StatusProjectFullSerializer


class ExtractivismTypeViewSet(BaseViewSet):
    queryset = ExtractivismType.objects.all()
    serializer_class = ExtractivismTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ExtractivismTypeSerializer,
            'create': ExtractivismTypeSerializer,
            'update': ExtractivismTypeSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)


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
