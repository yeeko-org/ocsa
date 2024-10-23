from rest_framework import viewsets, permissions
from django_filters import FilterSet, NumberFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.pagination import CustomPagination
from rest_framework.decorators import action

from rest_framework.response import Response

from actor.models import Actor, Participant
from api.merge_mix import FromToModelSerializer, MergeSerializerMixin
from classify.models import (
    ParticipantType,
    Belong,
    IndigenousGroup,
    SectorGroup,
    Sector,
    InterestGroup,
    InterestType
)
from event.models import (
    EventGroup,
    EventType,
    EventSubtype,
    InvolvedRole,)

from impact.models import ImpactSubtype, ImpactType
from profile_auth.models import Role
from source.models import Source
from work_flux.models import StatusControl

from space_time.models import StatusProject
from project.models import MegaprojectType, Project, ExtractivismType

from api.views.catalogs.event_serializers import (
    EventGroupSerializer,
    EventTypeSerializer,
    EventSubtypeSerializer,
    InvolvedRoleSerializer)

from api.views.catalogs.classify_serializers import (
    ParticipantTypeSerializer,
    BelongSerializer,
    IndigenousGroupSerializer,
    SectorGroupSerializer,
    SectorSerializer,
    InterestGroupSerializer,
    InterestTypeSerializer,
)
from api.views.catalogs.serializers import (
    ImpactSubtypeSerializer,
    ImpactTypeSerializer,
    RoleSerializer,
    SourceSerializer,
    StatusControlSerializer,

    StatusProjectSerializer,
)
from api.views.catalogs.project_serializers import (
    ExtractivismTypeSerializer,
    MegaprojectTypeCountSerializer,
    MegaprojectTypeFullSerializer,
)
from .all import CatalogsView  # noqa


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


class IndigenousGroupViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = IndigenousGroup.objects.all()
    serializer_class = IndigenousGroupSerializer

    def get_from_obj(self, from_id):
        return IndigenousGroup.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Actor.objects.filter(indigenous_group=from_obj)\
            .update(indigenous_group=to_obj)


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


class EventGroupViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = EventGroup.objects.all()
    serializer_class = EventGroupSerializer


class EventTypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer


class EventSubtypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = EventSubtype.objects.all()
    serializer_class = EventSubtypeSerializer


class InvolvedRoleViewSet(viewsets.ModelViewSet):
    # from django.db.models import Count, F
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = InvolvedRole.objects.all()
    # .annotate(
    #     event_group=F('event_type__event_group')
    # )
    serializer_class = InvolvedRoleSerializer


class ImpactSubtypeFilter(FilterSet):

    class Meta:
        model = ImpactSubtype
        fields = {'impact_type': ['exact']}


class ImpactSubtypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    from django.db.models import Count

    permission_classes = [permissions.AllowAny]
    queryset = ImpactSubtype.objects.all()
    serializer_class = ImpactSubtypeSerializer


class ImpactTypeViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = ImpactType.objects.all()
    serializer_class = ImpactTypeSerializer


class RoleViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


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


class StatusProjectViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = StatusProject.objects.all()
    serializer_class = StatusProjectSerializer


# class ExtractivismTypeViewSet(viewsets.ModelViewSet):
#     # permission_classes = [permissions.IsAuthenticated]
#     permission_classes = [permissions.AllowAny]
#     queryset = ExtractivismType.objects.all()
#     serializer_class = ExtractivismTypeSerializer


class MegaprojectTypeFilter(FilterSet):
    extractivism_type = NumberFilter(
        field_name='extractivism_types', lookup_expr='exact')

    class Meta:
        model = MegaprojectType
        fields = {'status_validation': ['exact']}


class MegaprojectTypeViewSet(viewsets.ModelViewSet):
    # from django.db.models import Count, F
    from django.db.models import Count

    queryset = MegaprojectType.objects.all()\
        .annotate(count=Count('projects'))\
        .prefetch_related('extractivism_types', 'projects', 'status_validation')\
        .distinct()
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    pagination_class = CustomPagination
    filterset_class = MegaprojectTypeFilter
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['name', 'count', 'status_validation__order']

    serializer_class = MegaprojectTypeCountSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': MegaprojectTypeFullSerializer,
            'create': MegaprojectTypeCountSerializer,
            'update': MegaprojectTypeCountSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
