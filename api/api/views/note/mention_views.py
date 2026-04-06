from django_filters import FilterSet, NumberFilter
from rest_framework import viewsets, status
from rest_framework.response import Response
from api.views.common_views import (
    BaseStatusViewSet, ClickHistoryMixin, BaseGenericViewSet,
)
from api.views.note.serializers import (
    MentionSimpleSerializer, MentionMegaFullSerializer,
    InterestSerializer,
    StatusHistorySerializer, StatusHistoryFullSerializer,
    ParticipantFullSerializer,
    ParticipantMegaFullSerializer,
    ParticipantListFullSerializer,
)
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
    ClickHistoryMixin, BaseGenericViewSet,
):
    queryset = Participant.objects.all()

    filterset_class = ParticipantFilter
    serializer_class = ParticipantFullSerializer
    is_mention_child = True
    ordering = ['actor__name']

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ParticipantMegaFullSerializer,
            'list': ParticipantListFullSerializer,
        }
        return action_serializer.get(
            self.action, self.serializer_class,
        )


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


