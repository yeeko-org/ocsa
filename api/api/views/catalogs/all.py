
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from classify.models import (
    ParticipantType,
    ParticipantGroup,
    Belong,
    IndigenousGroup,
    SectorGroup,
    Sector,
    InterestGroup,
    InterestType,
    InterestSubtype,
    Country,
)
from event.models import (
    EventGroup,
    EventType,
    EventSubtype,
    InvolvedRole,)
from profile_auth.models import User
from ps_schema.models import Level, Collection, FilterGroup

from space_time.models import State
from project.models import MegaprojectType, ExtractivismType, StatusProject

from impact.models import ImpactSubtype, ImpactType, ImpactGroup
from source.models import Source
from work_flux.models import StatusControl

from api.views.catalogs.serializers import (
    ImpactGroupSerializer,
    ImpactSubtypeSimpleSerializer,
    ImpactTypeSimpleSerializer,
    SourceSerializer,
    StatusControlSerializer,
    LevelSerializer,
    CollectionSerializer,
    FilterGroupSerializer,
)
from api.views.auth.serializers import UserProfileSerializer
from api.views.catalogs import StatusProjectSerializer
from api.views.catalogs.project_serializers import (
    MegaprojectTypeSerializer,
    ExtractivismTypeSerializer)
from api.views.catalogs.classify_serializers import (
    ParticipantTypeSerializer,
    ParticipantGroupSerializer,
    BelongSerializer,
    SectorGroupSerializer,
    SectorSerializer,
    InterestGroupSerializer,
    InterestTypeSerializer,
    InterestSubtypeSerializer,
    IndigenousGroupSerializer, CountrySerializer,
)

from api.views.catalogs.event_serializers import (
    EventGroupSerializer,
    EventTypeSerializer,
    EventSubtypeSerializer,
    InvolvedRoleSerializer,
)
from api.views.space_time.serializers import (
    StateListSerializer,
)
from actor.models import Actor


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        sectors = Sector.objects\
            .filter(name__isnull=False)\
            .exclude(name__exact='')
        networks = Actor.objects\
            .filter(network_seq__isnull=False)\
            .values_list('network_seq', flat=True)\
            .distinct()
        # print("networks", networks)
        network_list_sorted = sorted(list(networks))
        final_networks = [{"name": f"Red {i}", "id": i}
                          for i in network_list_sorted]
        catalogs = {
            "user": UserProfileSerializer(
                User.objects.all(), many=True).data,
            "participant_type": ParticipantTypeSerializer(
                ParticipantType.objects.all(), many=True).data,
            "participant_group": ParticipantGroupSerializer(
                ParticipantGroup.objects.all(), many=True).data,
            "belong": BelongSerializer(
                Belong.objects.all(), many=True).data,
            "indigenous_group": IndigenousGroupSerializer(
                IndigenousGroup.objects.all(), many=True).data,
            "sector_group": SectorGroupSerializer(
                SectorGroup.objects.all(), many=True).data,
            "sector": SectorSerializer(sectors, many=True).data,
            "country": CountrySerializer(
                Country.objects.all(), many=True).data,
            "network": final_networks,

            "interest_group": InterestGroupSerializer(
                InterestGroup.objects.all(), many=True).data,
            "interest_type": InterestTypeSerializer(
                InterestType.objects.all(), many=True).data,
            "interest_subtype": InterestSubtypeSerializer(
                InterestSubtype.objects.all(), many=True).data,

            "event_group": EventGroupSerializer(
                EventGroup.objects.all(), many=True).data,
            "event_type": EventTypeSerializer(
                EventType.objects.all(), many=True).data,
            "event_subtype": EventSubtypeSerializer(
                EventSubtype.objects.all(), many=True).data,
            "involved_role": InvolvedRoleSerializer(
                InvolvedRole.objects.all(), many=True).data,

            "impact_group": ImpactGroupSerializer(
                ImpactGroup.objects.all(), many=True).data,
            "impact_subtype": ImpactSubtypeSimpleSerializer(
                ImpactSubtype.objects.all(), many=True).data,
            "impact_type": ImpactTypeSimpleSerializer(
                ImpactType.objects.all(), many=True).data,

            "megaproject_type": MegaprojectTypeSerializer(
                MegaprojectType.objects.all(), many=True).data,
            "extractivism_type": ExtractivismTypeSerializer(
                ExtractivismType.objects.all(), many=True).data,
            # "status_project": StatusProjectSerializer(
            #     StatusProject.objects.all(), many=True).data,
            "status_project": StatusProjectSerializer(
                StatusProject.objects.all(), many=True).data,

            "source": SourceSerializer(
                Source.objects.all(), many=True).data,
            "status_control": StatusControlSerializer(
                StatusControl.objects.all(), many=True).data,
            "state": StateListSerializer(
                State.objects.all(), many=True).data,

            "levels": LevelSerializer(
                Level.objects.all(), many=True).data,
            "collections": CollectionSerializer(
                Collection.objects.all(), many=True).data,
            "filter_groups": FilterGroupSerializer(
                FilterGroup.objects.all(), many=True).data,
        }
        return Response(catalogs)
