from rest_framework import viewsets, permissions
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
    EventRole,)

from impact.models import ImpactSubtype, ImpactType
from profile_auth.models import Role
from source.models import Source
from work_flux.models import StatusControl

from space_time.models import StatusProject

from api.views.catalogs.serializers import (
    ParticipantTypeSerializer,
    BelongSerializer,
    IndigenousGroupSerializer,
    SectorGroupSerializer,
    SectorSerializer,
    InterestGroupSerializer,
    InterestTypeSerializer,
    EventGroupSerializer,
    EventTypeSerializer,
    EventSubtypeSerializer,
    EventRoleSerializer,
    ImpactSubtypeSerializer,
    ImpactTypeSerializer,
    RoleSerializer,
    SourceSerializer,
    StatusControlSerializer,
    StatusProjectSerializer
)

from .all import CatalogsView  # noqa


class ParticipantTypeViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
    queryset = IndigenousGroup.objects.all()
    serializer_class = IndigenousGroupSerializer

    def get_from_obj(self, from_id):
        return IndigenousGroup.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Actor.objects.filter(indigenous_group=from_obj)\
            .update(indigenous_group=to_obj)


class SectorGroupViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SectorGroup.objects.all()
    serializer_class = SectorGroupSerializer

    def get_from_obj(self, from_id):
        return SectorGroup.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Sector.objects.filter(sector_group=from_obj)\
            .update(sector_group=to_obj)


class SectorViewSet(MergeSerializerMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer

    def get_from_obj(self, from_id):
        return Sector.objects.get(id=from_id)
    
    def update_relations_merge(self, from_obj, to_obj):
        Actor.objects.filter(sector=from_obj)\
            .update(sector=to_obj)



class InterestGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = InterestGroup.objects.all()
    serializer_class = InterestGroupSerializer


class InterestTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = InterestType.objects.all()
    serializer_class = InterestTypeSerializer


class EventGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = EventGroup.objects.all()
    serializer_class = EventGroupSerializer


class EventTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer


class EventSubtypeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = EventSubtype.objects.all()
    serializer_class = EventSubtypeSerializer


class EventRoleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = EventRole.objects.all()
    serializer_class = EventRoleSerializer


class ImpactSubtypeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ImpactSubtype.objects.all()
    serializer_class = ImpactSubtypeSerializer


class ImpactTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ImpactType.objects.all()
    serializer_class = ImpactTypeSerializer


class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class SourceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class StatusControlViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StatusControl.objects.all()
    serializer_class = StatusControlSerializer


class StatusProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StatusProject.objects.all()
    serializer_class = StatusProjectSerializer
