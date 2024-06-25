
from rest_framework.views import APIView
from rest_framework.response import Response

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
    StatusControlSerializer
)


class CatalogsView(APIView):
    def get(self, request):
        catalogs = {
            "participant_types": ParticipantTypeSerializer(ParticipantType.objects.all(), many=True).data,
            "belongs": BelongSerializer(Belong.objects.all(), many=True).data,
            "indigenous_groups": IndigenousGroupSerializer(IndigenousGroup.objects.all(), many=True).data,
            "sector_groups": SectorGroupSerializer(SectorGroup.objects.all(), many=True).data,
            "sectors": SectorSerializer(Sector.objects.all(), many=True).data,
            "interest_groups": InterestGroupSerializer(InterestGroup.objects.all(), many=True).data,
            "interest_types": InterestTypeSerializer(InterestType.objects.all(), many=True).data,
            "event_groups": EventGroupSerializer(EventGroup.objects.all(), many=True).data,
            "event_types": EventTypeSerializer(EventType.objects.all(), many=True).data,
            "event_subtypes": EventSubtypeSerializer(EventSubtype.objects.all(), many=True).data,
            "event_roles": EventRoleSerializer(EventRole.objects.all(), many=True).data,
            "impact_subtypes": ImpactSubtypeSerializer(ImpactSubtype.objects.all(), many=True).data,
            "impact_types": ImpactTypeSerializer(ImpactType.objects.all(), many=True).data,
            "roles": RoleSerializer(Role.objects.all(), many=True).data,
            "sources": SourceSerializer(Source.objects.all(), many=True).data,
            "status_controls": StatusControlSerializer(StatusControl.objects.all(), many=True).data,
        }
        return Response(catalogs)
