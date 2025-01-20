from rest_framework import viewsets, permissions
from django_filters import FilterSet, NumberFilter
from django.db.models import Count
# from rest_framework.decorators import action
# from rest_framework.response import Response

from classify.models import (
    InterestGroup,
    InterestType,
    InterestSubtype, )
from event.models import (
    InvolvedRole,)

from source.models import Source
from work_flux.models import StatusControl

from project.models import MegaprojectType, ExtractivismType, StatusProject

from api.views.catalogs.event_serializers import InvolvedRoleSerializer

from api.views.catalogs.classify_serializers import (
    InterestGroupSerializer, InterestTypeSerializer,
    InterestSubtypeSerializer
)
from api.views.catalogs.serializers import (
    SourceSerializer, SourceFullSerializer,
    StatusControlSerializer,
)
from api.views.catalogs.project_serializers import (
    ExtractivismTypeSerializer,
    MegaprojectTypeCountSerializer,
    MegaprojectTypeFullSerializer,
    StatusProjectSerializer,
)
from .all import CatalogsView  # noqa
from ..common_views import BaseViewSet, BaseStatusViewSet


class InterestGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = InterestGroup.objects.all()
    serializer_class = InterestGroupSerializer


class InterestTypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = InterestType.objects.all()
    serializer_class = InterestTypeSerializer


class InterestSubtypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = InterestSubtype.objects.all()
    serializer_class = InterestSubtypeSerializer


class InvolvedRoleViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = InvolvedRole.objects.all()
    # .annotate(
    #     event_group=F('event_type__event_group')
    # )
    serializer_class = InvolvedRoleSerializer


class SourceViewSet(BaseStatusViewSet):

    filterset_fields = []
    queryset = Source.objects.all()\
        .annotate(notes_count=Count('notes'))\
        .distinct()
    serializer_class = SourceFullSerializer


class StatusControlViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = StatusControl.objects.all()
    serializer_class = StatusControlSerializer


class StatusProjectViewSet(BaseStatusViewSet):
    queryset = StatusProject.objects.all()\
        .annotate(count=Count('projects'))\
        .distinct()
    serializer_class = StatusProjectSerializer


class ExtractivismTypeViewSet(BaseViewSet):
    queryset = ExtractivismType.objects.all()
    serializer_class = ExtractivismTypeSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ExtractivismTypeSerializer,
            'create': ExtractivismTypeSerializer,
            'update': ExtractivismTypeSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)


class MegaprojectTypeFilter(FilterSet):
    extractivism_type = NumberFilter(
        field_name='extractivism_types', lookup_expr='exact')

    class Meta:
        model = MegaprojectType
        fields = {'status_validation': ['exact']}


class MegaprojectTypeViewSet(BaseStatusViewSet):

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
