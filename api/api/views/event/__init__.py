from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from api.pagination import CustomPagination
from api.views.action_export_xls import ExportXlsMixin
from api.views.common_views import ClickHistoryMixin, MassiveEdit

from api.views.event.serializers import EventSerializer, EventMediumSerializer
from api.views.note.serializers import EventFullNoteSerializer
from event.models import Event


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
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_export_rows(self, queryset) -> list[dict]:
        from api.export_blocks.event import EventExportBlock
        from api.export_blocks.mention import MentionExportBlock
        from api.export_blocks.location import LocationExportBlock

        return [
            {
                **EventExportBlock.extract(event),
                **MentionExportBlock.extract(event),
                **LocationExportBlock.extract(event),
            }
            for event in queryset
        ]

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
