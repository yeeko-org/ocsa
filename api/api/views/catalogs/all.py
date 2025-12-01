from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ps_schema.models import Level, Collection, FilterGroup
from impact.models import ImpactSubtype, ImpactType, ImpactGroup
from source.models import Source, DiscardedReason
from work_flux.models import StatusControl
from space_time.models import State
from api.views.catalogs.serializers import (
    ImpactGroupSerializer,
    ImpactSubtypeSimpleSerializer,
    ImpactTypeSimpleSerializer,
    SourceSerializer,
    DiscardedReasonSerializer,
    StatusControlSerializer,
    LevelSerializer,
    CollectionSerializer,
    FilterGroupSerializer,
    StateListSerializer,
)

from profile_auth.models import User
from api.views.auth.serializers import UserProfileSerializer

from project.models import (
    MegaprojectType, ExtractivismType, StatusProject)
from api.views.catalogs.project_serializers import (
    MegaprojectTypeSerializer, ExtractivismTypeSerializer,
    StatusProjectSerializer)

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

from event.models import (
    EventGroup,
    EventType,
    InvolvedRole,
    Purpose)
from api.views.catalogs.event_serializers import (
    EventGroupSerializer,
    EventTypeSerializer,
    InvolvedRoleSerializer,
    PurposeSerializer,
)

from df.models import Dimension, PopulationSize, Temporality
from api.views.catalogs.df_serializers import (
    DimensionSerializer, PopulationSizeSerializer, TemporalitySerializer)

from actor.models import Actor


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        networks = Actor.objects\
            .filter(network_seq__isnull=False)\
            .values_list('network_seq', flat=True)\
            .distinct()
        # print("networks", networks)
        network_list_sorted = sorted(list(networks))
        final_networks = [{"name": f"Red {i}", "id": i}
                          for i in network_list_sorted]
        megaproject_types = MegaprojectType.objects.all()\
            .prefetch_related("extractivism_types")
        catalogs = {
            # cortos: 56 ms (183 kb)
            # con largos: 450 ms (303 kb)

            # 30 ms
            "user": UserProfileSerializer(
                User.objects.all(), many=True).data,

            # 42 ms
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
            "sector": SectorSerializer(
                Sector.objects.all(), many=True).data,
            "country": CountrySerializer(
                Country.objects.all(), many=True).data,

            # 28 ms
            "network": final_networks,

            # 34 ms
            "interest_group": InterestGroupSerializer(
                InterestGroup.objects.all(), many=True).data,
            "interest_type": InterestTypeSerializer(
                InterestType.objects.all(), many=True).data,
            "interest_subtype": InterestSubtypeSerializer(
                InterestSubtype.objects.all(), many=True).data,

            # 63 ms
            "event_group": EventGroupSerializer(
                EventGroup.objects.all(), many=True).data,
            # has_count
            "event_type": EventTypeSerializer(
                EventType.objects.all(), many=True).data,
            # has_count
            "purpose": PurposeSerializer(
                Purpose.objects.all(), many=True).data,
            "involved_role": InvolvedRoleSerializer(
                InvolvedRole.objects.all(), many=True).data,

            # 28 ms
            "dimension": DimensionSerializer(
                Dimension.objects.all(), many=True).data,
            "population_size": PopulationSizeSerializer(
                PopulationSize.objects.all(), many=True).data,
            "temporality": TemporalitySerializer(
                Temporality.objects.all(), many=True).data,

            # 32 ms
            "impact_group": ImpactGroupSerializer(
                ImpactGroup.objects.all(), many=True).data,
            "impact_subtype": ImpactSubtypeSimpleSerializer(
                ImpactSubtype.objects.all(), many=True).data,
            "impact_type": ImpactTypeSimpleSerializer(
                ImpactType.objects.all(), many=True).data,

            # 54 ms
            "megaproject_type": MegaprojectTypeSerializer(
                megaproject_types, many=True).data,
            "extractivism_type": ExtractivismTypeSerializer(
                ExtractivismType.objects.all(), many=True).data,
            "status_project": StatusProjectSerializer(
                StatusProject.objects.all(), many=True).data,

            # 32 ms
            "source": SourceSerializer(
                Source.objects.all(), many=True).data,
            "discarded_reason": DiscardedReasonSerializer(
                DiscardedReason.objects.all(), many=True).data,
            "status_control": StatusControlSerializer(
                StatusControl.objects.all(), many=True).data,
            "state": StateListSerializer(
                State.objects.all(), many=True).data,

            # 44 ms
            "levels": LevelSerializer(
                Level.objects.all(), many=True).data,
            "collections": CollectionSerializer(
                Collection.objects.all(), many=True).data,
            "filter_groups": FilterGroupSerializer(
                FilterGroup.objects.all(), many=True).data,
        }
        return Response(catalogs)
