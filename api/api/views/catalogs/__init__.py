from rest_framework import viewsets, permissions
from django_filters import FilterSet, NumberFilter
from django.db.models import Count
# from rest_framework.decorators import action
# from rest_framework.response import Response

from actor.models import Actor, Participant
from api.merge_mix import MergeSerializerMixin
from classify.models import (
    ParticipantGroup,
    ParticipantType,
    Belong,
    SectorGroup,
    Sector,
    InterestGroup,
    InterestType,
    InterestSubtype, Country,
)
from event.models import (
    InvolvedRole,)

from impact.models import ImpactSubtype
from source.models import Source
from work_flux.models import StatusControl

from project.models import MegaprojectType, ExtractivismType, StatusProject

from api.views.catalogs.event_serializers import (
    EventGroupSerializer,
    EventTypeSerializer,
    EventTypeFullSerializer,
    EventSubtypeSerializer,
    EventSubtypeFullSerializer,
    InvolvedRoleSerializer)

from api.views.catalogs.classify_serializers import (
    ParticipantGroupSerializer,
    ParticipantTypeSerializer,
    BelongSerializer,
    SectorGroupSerializer,
    SectorSerializer,
    InterestGroupSerializer,
    InterestTypeSerializer,
    InterestSubtypeSerializer,
    CountrySerializer
)
from api.views.catalogs.serializers import (
    SourceSerializer,
    StatusControlSerializer,
)
from api.views.catalogs.project_serializers import (
    ExtractivismTypeFullSerializer,
    ExtractivismTypeSerializer,
    MegaprojectTypeCountSerializer,
    MegaprojectTypeFullSerializer, StatusProjectSerializer,
)
from .all import CatalogsView  # noqa
from ..common_views import BaseViewSet, BaseStatusViewSet
from ..space_time import ListSetMixin


class ParticipantTypeViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = ParticipantType.objects.all()
    serializer_class = ParticipantTypeSerializer

    def get_from_obj(self, from_id):
        return ParticipantType.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Participant.objects.filter(participant_type=from_obj)\
            .update(participant_type=to_obj)
        Sector.objects.filter(common_participant_types=from_obj)\
            .update(common_participant_types=to_obj)
        InterestGroup.objects.filter(participant_types=from_obj)\
            .update(participant_types=to_obj)


class BelongViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Belong.objects.all()
    serializer_class = BelongSerializer

    def get_from_obj(self, from_id):
        return Belong.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Actor.objects.filter(belongs=from_obj)\
            .update(belongs=to_obj)
        Sector.objects.filter(common_belongs=from_obj)\
            .update(common_belongs=to_obj)


class SectorGroupViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = SectorGroup.objects.all()
    serializer_class = SectorGroupSerializer

    def get_from_obj(self, from_id):
        return SectorGroup.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Sector.objects.filter(sector_group=from_obj)\
            .update(sector_group=to_obj)


class SectorViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer

    def get_from_obj(self, from_id):
        return Sector.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Actor.objects.filter(sector=from_obj)\
            .update(sector=to_obj)


class CountryViewSet(ListSetMixin):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class ParticipantGroupViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = ParticipantGroup.objects.all()
    serializer_class = ParticipantGroupSerializer


class InterestGroupViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
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


class SourceViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


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
            'retrieve': ExtractivismTypeFullSerializer,
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


class MegaprojectTypeViewSet(BaseViewSet):

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
