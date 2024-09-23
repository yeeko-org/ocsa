from django_filters import FilterSet, DateFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter


from event.models import Event

from api.pagination import CustomPagination
from api.views.event.serializers import (
    EventSerializer, EventCreateSerializer, EventFullSerializer)


class EventFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    event_subtype = NumberFilter(
        field_name='event_type__event_subtype', lookup_expr='exact')

    class Meta:
        model = Event
        fields = {
            'event_type': ['exact']
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

    search_fields = [
        "description",
    ]
    ordering_fields = ['id', 'date']
    ordering = ['id']

    serializer_class = EventSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': EventFullSerializer,
            'create': EventCreateSerializer,
            'update': EventCreateSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)

