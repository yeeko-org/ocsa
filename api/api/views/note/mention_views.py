from django_filters import FilterSet, DateFilter, NumberFilter
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.views.common_views import BaseViewSet, UnaccentSearchFilter
from api.pagination import CustomPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from api.views.event import EventSerializer, EventFullSerializer, EventCreateSerializer
from api.views.note.serializers import (
    MentionSerializer, MentionMegaFullSerializer,
    ParticipantSimpleSerializer, InterestSerializer,
    InvolvedSerializer, StatusHistorySerializer)
from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantSerializer)
from api.views.note.serializers import ImpactFullSerializer, EventFullNoteSerializer

from source.models import Mention, StatusHistory
from actor.models import Participant, Interest
from impact.models import Impact
from event.models import Involved, Event


class MentionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Mention.objects.all()

    serializer_class = MentionSerializer

    def common(self, request, serializer):

        if serializer.is_valid():
            serializer.save()

            new_serializer = MentionMegaFullSerializer(
                serializer.instance)
            return Response(
                new_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        return self.common(request, serializer)

    def update(self, request, *args, **kwargs):

        mention = self.get_object()
        serializer = self.get_serializer(mention, data=request.data)
        return self.common(request, serializer)


class ParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Participant.objects.all()

    serializer_class = ParticipantSimpleSerializer

    def create(self, request, *args, **kwargs):

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            new_serializer = ParticipantSerializer(
                serializer.instance)
            return Response(
                new_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImpactViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPagination
    queryset = Impact.objects.all()

    serializer_class = ImpactSerializer
    filter_backends = [UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['description']
    filterset_fields = ['impact_type', 'impact_subtype']

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ImpactFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class InterestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Interest.objects.all()

    serializer_class = InterestSerializer


class InvolvedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Involved.objects.all()

    serializer_class = InvolvedSerializer


class StatusHistoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = StatusHistory.objects.all()

    serializer_class = StatusHistorySerializer


class EventFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    event_type = NumberFilter(
        field_name='event_subtype__event_types', lookup_expr='exact')

    class Meta:
        model = Event
        fields = {
            'event_subtype': ['exact']
        }


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()\
        .select_related(
            'event_type',
            'mention',
            'mention__note',
            'mention__project',
        )\
        .prefetch_related(
            'involvements',
            'involvements__participant',
            'involvements__participant__actor',

        )
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    pagination_class = CustomPagination

    filterset_class = EventFilter

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]

    search_fields = ["description", "event_subtype__name"]
    ordering_fields = ['id', 'date']
    ordering = ['id']

    serializer_class = EventSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': EventFullNoteSerializer,
            # 'retrieve': EventFullSerializer,
            'create': EventCreateSerializer,
            'update': EventCreateSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
