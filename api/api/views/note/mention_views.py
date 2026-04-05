from django_filters import FilterSet, NumberFilter
from rest_framework import viewsets, status
from rest_framework.response import Response
from api.views.common_views import BaseStatusViewSet
from api.views.action_export_xls import ExportXlsMixin

from api.views.note.serializers import (
    MentionSimpleSerializer, MentionMegaFullSerializer,
    InterestSerializer,
    StatusHistorySerializer, StatusHistoryFullSerializer,
    ParticipantFullSerializer,
    ParticipantMegaFullSerializer, ParticipantListFullSerializer)
from api.export_blocks.participant import ParticipantExportBlock
from api.views.common_views import ClickHistoryMixin
from api.views.common_views import BaseGenericViewSet

from source.models import Mention, StatusHistory
from actor.models import Participant, Interest


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
    xls_attrs = [
        {"special_group": "participant"},
        {"special_group": "mention"},
    ]

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ParticipantMegaFullSerializer,
            'list': ParticipantListFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_export_rows(self, queryset) -> list[dict]:
        from api.export_blocks.mention import MentionExportBlock
        return [
            {
                **ParticipantExportBlock.extract(p),
                **MentionExportBlock.extract(p),
            }
            for p in queryset
        ]

    def get_query_for_export_xls(self):

        queryset = self.get_queryset() \
            .select_related(
            'mention',
            'mention__note',
            'mention__note__source',
            'mention__project',
            'mention__project__conflict',
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


class InterestViewSet(BaseGenericViewSet):

    queryset = Interest.objects.all()
    filterset_fields = ['interest_subtype']
    search_fields = ["text"]

    serializer_class = InterestSerializer


class StatusHistoryViewSet(BaseStatusViewSet):
    filterset_fields = ['status_project']
    queryset = StatusHistory.objects.all()\
        .select_related('mention__project', 'mention__note')

    serializer_class = StatusHistoryFullSerializer

    def get_serializer_class(self):
        action_serializer = {'list': StatusHistorySerializer}
        return action_serializer.get(self.action, self.serializer_class)


