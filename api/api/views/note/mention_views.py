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
    MentionSimpleSerializer, MentionMegaFullSerializer,
    ParticipantSimpleSerializer, InterestSerializer,
    InvolvedSerializer, StatusHistorySerializer, StatusHistoryFullSerializer,
    ParticipantFullSerializer,
    ParticipantMegaFullSerializer, ParticipantListFullSerializer)
from api.views.actor.participant_export import (
    ParticipantExportLoggedSerializer, ParticipantExportSerializer,
    xlsx_participant_fields)
from api.views.project.list_serializers import (
    ImpactSerializer, ImpactSimpleSerializer)
from api.views.note.serializers import (
    ImpactFullSerializer, EventFullNoteSerializer)
from api.views.event.serializers import (
    EventExportFullSerializer, ImpactExportSerializer, EventMediumSerializer)
from api.views.common_views import MassiveEdit, ClickHistoryMixin
from api.views.common_views import BaseGenericViewSet

from source.models import Mention, StatusHistory
from actor.models import Participant, Interest
from impact.models import Impact
from event.models import Involved, Event


class MentionViewSet(ClickHistoryMixin, viewsets.ModelViewSet):
    queryset = Mention.objects.all()

    serializer_class = MentionSimpleSerializer


    def get_serializer_class(self):
        # print("self.action", self.action)
        action_serializer = {
            'retrieve': MentionMegaFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

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
        self.save_click_action(request, mention.note, 'updated', force=True)
        serializer = self.get_serializer(mention, data=request.data)
        return self.common(request, serializer)


class ParticipantFilter(FilterSet):

    event_type = NumberFilter(
        field_name='involvements__event__event_type',
        lookup_expr='exact')
    # indirect_event_type = NumberFilter(
    #     field_name='mention__events__event_type',
    #     lookup_expr='exact')

    class Meta:
        model = Participant
        fields = {
            # 'event_type': ['exact'],
            # 'purpose': ['exact'],
        }

class ParticipantViewSet(
    ClickHistoryMixin, ExportXlsMixin, BaseGenericViewSet):
    queryset = Participant.objects.all()

    filterset_class = ParticipantFilter
    serializer_class = ParticipantFullSerializer
    is_mention_child = True
    ordering = ['actor__name']
    # additional_groups = ["actor", "mention"]
    xls_attrs = xlsx_participant_fields

    def get_serializer_class(self):
        # user_object = self.request.user if self.request else None
        is_authenticated = self.request.user.is_authenticated \
            if self.request else False
        export_serializer = ParticipantExportLoggedSerializer \
            if is_authenticated else ParticipantExportSerializer
        action_serializer = {
            'export_xls': export_serializer,
            'retrieve': ParticipantMegaFullSerializer,
            'list': ParticipantListFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


    def get_query_for_export_xls(self):

        queryset = self.get_queryset() \
            .select_related(
            'mention',
            'mention__note',
            'mention__note__source',
            'mention__project',
            'actor',
            'actor__parent_actor',
            'actor__sector',
            'actor__sector__sector_group',
            'actor__indigenous_group',
        )\
        .prefetch_related(
            'interests',
            'interests__interest_subtype',
            'interests__interest_subtype__interest_type',
            'interests__interest_subtype__interest_type__interest_group',
            'actor__belongs',
            'actor__countries',
        ) \
        .order_by('-id')\
        .distinct()
        return self.filter_queryset(queryset)


class ImpactViewSet(
    ClickHistoryMixin, MassiveEdit, ExportXlsMixin, viewsets.ModelViewSet
):
    pagination_class = CustomPagination
    queryset = Impact.objects.all()
    is_mention_child = True

    xls_attrs = [
        {
            "name": "ID",
            "width": 5,
            "field": "id"
        },
        {
            "name": "Descripción de la afectación",
            "width": 50,
            "field": "description"
        },
        {
            "name": "Grupo de afectación",
            "width": 15,
            "field": "impact_type__impact_group"
        },
        {
            "name": "Tipo de afectación",
            "width": 15,
            "field": "impact_type__name"
        },
        {
            "name": "Subtipo de afectación",
            "width": 30,
            "field": "impact_subtype__name"
        },
    ]

    # add_locations = True
    additional_groups = ["mention", "location"]
    serializer_class = ImpactSimpleSerializer
    filter_backends = [UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['description']
    filterset_fields = ['impact_type', 'impact_subtype']

    def get_serializer_class(self):
        # print("self.action", self.action)
        action_serializer = {
            'retrieve': ImpactFullSerializer,
            'update': ImpactFullSerializer,
            'create': ImpactFullSerializer,
            'export_xls': ImpactExportSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_query_for_export_xls(self):

        annotations = self.get_annotations(target='impact')

        queryset = self.get_queryset() \
            .annotate(**annotations)\
            .select_related(
                'mention', 'mention__note',
                'mention__note__source',
                'mention__project', 'mention__project__conflict',
                'impact_subtype',
                'impact_type', 'impact_type__impact_group',
            )\
            .distinct()

        return self.filter_queryset(queryset)


class InterestViewSet(BaseGenericViewSet):

    queryset = Interest.objects.all()
    filterset_fields = ['interest_subtype']
    search_fields = ["text"]

    serializer_class = InterestSerializer


class InvolvedViewSet(viewsets.ModelViewSet):
    queryset = Involved.objects.all()

    serializer_class = InvolvedSerializer


    def get_query_for_export_xls(self):

        queryset = self.get_queryset() \
            .select_related(
            'event',
            'event__purpose',
            'event__event_type',
            'event__event_type__event_group',
            'event__mention',
            'event__mention__note',
            'event__mention__note__source',
            'event__mention__project',
            'participant__actor',
            'participant__actor__parent_actor',
            'participant__actor__sector',
            'participant__actor__sector__sector_group',
            'participant__actor__indigenous_group',
            'actor__belongs',
            'actor__countries',
        )\
        .order_by('-id')\
        .distinct()
        return self.filter_queryset(queryset)[:100]


class StatusHistoryViewSet(BaseStatusViewSet):
    filterset_fields = ['status_project']
    queryset = StatusHistory.objects.all()\
        .select_related('mention__project', 'mention__note')

    serializer_class = StatusHistoryFullSerializer

    def get_serializer_class(self):
        action_serializer = {'list': StatusHistorySerializer}
        return action_serializer.get(self.action, self.serializer_class)


class EventFilter(FilterSet):

    event_group = NumberFilter(
        field_name='event_type__event_group', lookup_expr='exact')
    sector_group = NumberFilter(
        field_name='involvements__participant__actor__sector__sector_group',
        lookup_expr='exact')
    sector = NumberFilter(
        field_name='involvements__participant__actor__sector',
        lookup_expr='exact')
    participant_type = NumberFilter(
        field_name='involvements__participant__participant_types',
        lookup_expr='exact')
    participant_group = NumberFilter(
        field_name='involvements__participant__participant_types__participant_group',
        lookup_expr='exact')
    involved_role = NumberFilter(
        field_name='involvements__involved_role',
        lookup_expr='exact')
    actor = NumberFilter(
        field_name='involvements__participant__actor',
        lookup_expr='exact')
    indirect_actor = NumberFilter(
        field_name='mention__participants__actor',
        lookup_expr='exact')
    project = NumberFilter(
        field_name='mention__project', lookup_expr='exact')

    class Meta:
        model = Event
        fields = {
            'event_type': ['exact'],
            'purpose': ['exact'],
        }


class EventViewSet(
    ClickHistoryMixin, MassiveEdit, ExportXlsMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all()\
        .select_related(
            'mention',
            'mention__note',
            'mention__project',
        )\
        .prefetch_related(
            'involvements',
        )\
        .distinct()

    serializer_class = EventSerializer
    is_mention_child = True

    pagination_class = CustomPagination
    filterset_class = EventFilter

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]

    search_fields = ["description"]
    ordering_fields = ['id', 'date']
    ordering = ['id']

    # add_locations = True
    # additional_groups = ["mention", "location"]
    xls_name = 'Eventos'
    xls_attrs = [
        {
            "special_group": "event",
        },
        {
            "special_group": "mention",
        },
        {
            "special_group": "location",
        },
    ]

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': EventFullNoteSerializer,
            'create': EventMediumSerializer,
            'update': EventMediumSerializer,
            'export_xls': EventExportFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_queryset(self):
        queryset = super().get_queryset()
        action_is_detail = self.action in ['retrieve', 'list']
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
                'mention__note__source', 'purpose',
                'mention__project', 'mention__project__conflict',
                'event_type', 'event_type__event_group',
            )\
            .distinct()
        return self.filter_queryset(queryset)
