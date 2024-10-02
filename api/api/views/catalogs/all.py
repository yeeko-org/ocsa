
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

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

from space_time.models import State
from project.models import MegaprojectType, Scale, ExtractivismType

from impact.models import ImpactSubtype, ImpactType
from profile_auth.models import Role
from source.models import Source, StatusProject
from work_flux.models import StatusControl

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
    StatusProjectSerializer,
    StatusControlSerializer,
    MegaprojectTypeSerializer,
    ScaleSerializer,
    ExtractivismTypeSerializer
)

from api.views.space_time.serializers import StateListSerializer


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        sectors = Sector.objects\
            .filter(name__isnull=False)\
            .exclude(name__exact='')
        catalogs = {
            "participant_types": ParticipantTypeSerializer(
                ParticipantType.objects.all(), many=True).data,
            "belongs": BelongSerializer(
                Belong.objects.all(), many=True).data,
            "indigenous_groups": IndigenousGroupSerializer(
                IndigenousGroup.objects.all(), many=True).data,
            "sector_groups": SectorGroupSerializer(
                SectorGroup.objects.all(), many=True).data,
            "sectors": SectorSerializer(sectors, many=True).data,
            "interest_groups": InterestGroupSerializer(
                InterestGroup.objects.all(), many=True).data,
            "interest_types": InterestTypeSerializer(
                InterestType.objects.all(), many=True).data,
            "event_groups": EventGroupSerializer(
                EventGroup.objects.all(), many=True).data,
            "event_types": EventTypeSerializer(
                EventType.objects.all(), many=True).data,
            "event_subtypes": EventSubtypeSerializer(
                EventSubtype.objects.all(), many=True).data,
            "event_roles": EventRoleSerializer(
                EventRole.objects.all(), many=True).data,
            "impact_subtypes": ImpactSubtypeSerializer(
                ImpactSubtype.objects.all(), many=True).data,
            "impact_types": ImpactTypeSerializer(
                ImpactType.objects.all(), many=True).data,
            "roles": RoleSerializer(
                Role.objects.all(), many=True).data,
            "sources": SourceSerializer(
                Source.objects.all(), many=True).data,
            "status_project": StatusProjectSerializer(
                StatusProject.objects.all(), many=True).data,
            "status_control": StatusControlSerializer(
                StatusControl.objects.all(), many=True).data,
            "states": StateListSerializer(
                State.objects.all(), many=True).data,
            "megaproject_types": MegaprojectTypeSerializer(
                MegaprojectType.objects.all(), many=True).data,
            "scales": ScaleSerializer(
                Scale.objects.all(), many=True).data,
            "extractivism_types": ExtractivismTypeSerializer(
                ExtractivismType.objects.all(), many=True).data,
        }
        return Response(catalogs)
