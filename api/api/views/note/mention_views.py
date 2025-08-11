from django_filters import FilterSet, DateFilter, NumberFilter
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.views.common_views import BaseStatusViewSet, UnaccentSearchFilter
from api.pagination import CustomPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.views.action_export_xls import ExportXlsMixin

from api.views.event import EventSerializer
from api.views.note.serializers import (
    MentionSerializer, MentionMegaFullSerializer,
    ParticipantSimpleSerializer, InterestSerializer,
    InvolvedSerializer, StatusHistorySerializer, StatusHistoryFullSerializer)
from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantSerializer, ImpactSimpleSerializer)
from api.views.note.serializers import (
    ImpactFullSerializer, EventFullNoteSerializer)
from api.views.event.serializers import EventExportSerializer
from api.views.common_views import MassiveEdit

from source.models import Mention, StatusHistory
from actor.models import Participant, Interest
from impact.models import Impact
from event.models import Involved, Event


class MentionViewSet(viewsets.ModelViewSet):
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


class ImpactViewSet(MassiveEdit, viewsets.ModelViewSet):
    pagination_class = CustomPagination
    queryset = Impact.objects.all()

    serializer_class = ImpactSimpleSerializer
    filter_backends = [UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['description']
    filterset_fields = ['impact_type', 'impact_subtype']

    def get_serializer_class(self):
        print("self.action", self.action)
        action_serializer = {
            'retrieve': ImpactFullSerializer,
            'update': ImpactFullSerializer,
            'create': ImpactFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class InterestViewSet(viewsets.ModelViewSet):
    queryset = Interest.objects.all()

    serializer_class = InterestSerializer


class InvolvedViewSet(viewsets.ModelViewSet):
    queryset = Involved.objects.all()

    serializer_class = InvolvedSerializer


class StatusHistoryViewSet(BaseStatusViewSet):
    filterset_fields = ['status_project']
    queryset = StatusHistory.objects.all()

    serializer_class = StatusHistoryFullSerializer

    def get_serializer_class(self):
        action_serializer = {'list': StatusHistorySerializer}
        return action_serializer.get(self.action, self.serializer_class)


class EventFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    sector_group = NumberFilter(
        field_name='involvements__participant__actor__sector__sector_group',
        lookup_expr='exact')
    sector = NumberFilter(
        field_name='involvements__participant__actor__sector',
        lookup_expr='exact')
    involved_role = NumberFilter(
        field_name='involvements__involved_role',
        lookup_expr='exact')

    class Meta:
        model = Event
        fields = {
            'event_subtype': ['exact'],
            'event_type': ['exact'],
            'purpose': ['exact'],
        }


class EventViewSet(MassiveEdit, ExportXlsMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all()\
        .select_related(
            'mention',
            'mention__note',
            'mention__project',
        )\
        .prefetch_related(
            'involvements',
        )

    pagination_class = CustomPagination
    filterset_class = EventFilter

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]

    search_fields = ["description", "event_subtype__name"]
    ordering_fields = ['id', 'date']
    ordering = ['id']

    serializer_class = EventSerializer
    add_locations = True
    xls_attrs = [
        {
            "name": "ID",
            "width": 5,
            "field": "id"
        },
        {
            "name": "Descripción del evento",
            "width": 50,
            "field": "description"
        },
        {
            "name": "Mujeres víctimas",
            "width": 4,
            "field": "number_women"
        },
        {
            "name": "Hombres víctimas",
            "width": 4,
            "field": "number_men"
        },
        {
            "name": "Personas víctimas",
            "width": 4,
            "field": "number_mix"
        },
        {
            "name": "Grupo de evento",
            "width": 15,
            "field": "event_type__event_group"
        },
        {
            "name": "Tipo de evento",
            "width": 30,
            "field": "event_type__name"
        },
        {
            "name": "Subtipo de evento",
            "width": 25,
            "field": "event_subtype"
        },
        {
            "name": "ID de nota",
            "width": 5,
            "field": "mention__note_full__id"
        },
        {
            "name": "Fecha de nota",
            "width": 10,
            "field": "mention__note_full__date"
        },
        {
            "name": "Título de nota",
            "width": 40,
            "field": "mention__note_full__title"
        },
        # {
        #     "name": "Medio de la nota",
        #     "width": 15,
        #     "field": "mention__note_full__source"
        # },
        {
            "name": "ID de proyecto",
            "width": 5,
            "field": "mention__project_full__id"
        },
        {
            "name": "Nombre de proyecto",
            "width": 40,
            "field": "mention__project_full__name"
        },
        {
            "name": "ID de conflicto",
            "width": 5,
            "field": "conflict__id"
        },
        {
            "name": "Nombre de conflicto",
            "width": 30,
            "field": "conflict__name"
        },
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        action_is_detail = self.action in ['retrieve', 'create', 'update']
        if action_is_detail:
            return self.queryset.prefetch_related(
                'involvements__participant',
                'involvements__participant__actor')
        return queryset

    def get_query_for_export_xls(self):

        annotations = self.get_annotations(target='event')

        queryset = self.get_queryset() \
            .annotate(**annotations)\
            .select_related(
                'mention', 'mention__note',
                'mention__note__source',
                'mention__project', 'mention__project__conflict',
                'event_type', 'event_type__event_group', 'event_subtype'
            )\
            .distinct()
        return self.filter_queryset(queryset)

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': EventFullNoteSerializer,
            'create': EventFullNoteSerializer,
            'update': EventFullNoteSerializer,
            'export_xls': EventExportSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
