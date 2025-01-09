
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

from ps_schema.models import Level, Collection, CollectionLink, FilterGroup

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
    CollectionLinkSerializer,
    FilterGroupSerializer,
)
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
        print("networks", networks)
        network_list_sorted = sorted(list(networks))
        final_networks = [{"name": f"Red {i}", "id": i}
                          for i in network_list_sorted]
        catalogs = {
            "participant_types": ParticipantTypeSerializer(
                ParticipantType.objects.all(), many=True).data,
            "participant_groups": ParticipantGroupSerializer(
                ParticipantGroup.objects.all(), many=True).data,
            "belongs": BelongSerializer(
                Belong.objects.all(), many=True).data,
            "indigenous_groups": IndigenousGroupSerializer(
                IndigenousGroup.objects.all(), many=True).data,
            "sector_groups": SectorGroupSerializer(
                SectorGroup.objects.all(), many=True).data,
            "sectors": SectorSerializer(sectors, many=True).data,
            "countries": CountrySerializer(
                Country.objects.all(), many=True).data,
            "networks": final_networks,

            "interest_groups": InterestGroupSerializer(
                InterestGroup.objects.all(), many=True).data,
            "interest_types": InterestTypeSerializer(
                InterestType.objects.all(), many=True).data,
            "interest_subtypes": InterestSubtypeSerializer(
                InterestSubtype.objects.all(), many=True).data,

            "event_groups": EventGroupSerializer(
                EventGroup.objects.all(), many=True).data,
            "event_types": EventTypeSerializer(
                EventType.objects.all(), many=True).data,
            "event_subtypes": EventSubtypeSerializer(
                EventSubtype.objects.all(), many=True).data,
            "involved_roles": InvolvedRoleSerializer(
                InvolvedRole.objects.all(), many=True).data,

            "impact_groups": ImpactGroupSerializer(
                ImpactGroup.objects.all(), many=True).data,
            "impact_subtypes": ImpactSubtypeSimpleSerializer(
                ImpactSubtype.objects.all(), many=True).data,
            "impact_types": ImpactTypeSimpleSerializer(
                ImpactType.objects.all(), many=True).data,

            "megaproject_types": MegaprojectTypeSerializer(
                MegaprojectType.objects.all(), many=True).data,
            "extractivism_types": ExtractivismTypeSerializer(
                ExtractivismType.objects.all(), many=True).data,
            "status_project": StatusProjectSerializer(
                StatusProject.objects.all(), many=True).data,

            "sources": SourceSerializer(
                Source.objects.all(), many=True).data,
            "status_control": StatusControlSerializer(
                StatusControl.objects.all(), many=True).data,
            "states": StateListSerializer(
                State.objects.all(), many=True).data,

            "levels": LevelSerializer(
                Level.objects.all(), many=True).data,
            "collections": CollectionSerializer(
                Collection.objects.all(), many=True).data,
            "collection_links": CollectionLinkSerializer(
                CollectionLink.objects.all(), many=True).data,
            "filter_groups": FilterGroupSerializer(
                FilterGroup.objects.all(), many=True).data,
        }
        return Response(catalogs)
