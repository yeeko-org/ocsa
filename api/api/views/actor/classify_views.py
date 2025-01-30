from django.db.models import Count
from api.views.actor.classify_serializers import (
    IndigenousGroupSerializer, IndigenousGroupFullSerializer,
    SectorFullSerializer, SectorGroupSerializer,
    ParticipantGroupSerializer, ParticipantTypeSerializer,
    ParticipantGroupFullSerializer, BelongSerializer, CountrySerializer)
from api.views.common_views import BaseStatusViewSet
from classify.models import IndigenousGroup, Sector, SectorGroup, ParticipantGroup, ParticipantType, Belong, Country


class IndigenousGroupViewSet(BaseStatusViewSet):
    queryset = IndigenousGroup.objects.all()\
        .annotate(count=Count('actors'))\
        .distinct()

    serializer_class = IndigenousGroupSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': IndigenousGroupFullSerializer,
            'create': IndigenousGroupFullSerializer,
            'update': IndigenousGroupFullSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)


class SectorViewSet(BaseStatusViewSet):

    queryset = Sector.objects.all().annotate(actors_count=Count('actors'))
    serializer_class = SectorFullSerializer
    filterset_fields = ['status_validation', 'sector_group']


class SectorGroupViewSet(BaseStatusViewSet):

    queryset = SectorGroup.objects.all()\
        .annotate(sectors_count=Count('sectors'))\
        .distinct()
    serializer_class = SectorGroupSerializer


class ParticipantGroupViewSet(BaseStatusViewSet):
    queryset = ParticipantGroup.objects.all()\
        .annotate(participant_types_count=Count('participant_types'))\
        .distinct()
    filterset_fields = []
    serializer_class = ParticipantGroupFullSerializer

    def get_serializer_class(self):
        action_serializer = {
            'list': ParticipantGroupSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)


class ParticipantTypeViewSet(BaseStatusViewSet):
    queryset = ParticipantType.objects.all()\
        .annotate(actors_count=Count('participants__actor'))\
        .distinct()
    serializer_class = ParticipantTypeSerializer

    filterset_fields = ['status_validation', 'participant_group']


class BelongViewSet(BaseStatusViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    filterset_fields = []
    queryset = Belong.objects.all()\
        .annotate(actors_count=Count('actors'))\
        .distinct()
    serializer_class = BelongSerializer


class CountryViewSet(BaseStatusViewSet):
    queryset = Country.objects.all()\
        .annotate(actors_count=Count('actors'))\
        .distinct()
    filterset_fields = []
    serializer_class = CountrySerializer
