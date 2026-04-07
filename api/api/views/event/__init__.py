from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter

from api.pagination import CustomPagination
from api.views.common_views import ClickHistoryMixin, MassiveEdit

from api.views.event.serializers import (
    EventSerializer, EventMediumSerializer, InvolvedSerializer)
from api.views.common_views import BaseGenericViewSet
from api.views.note.serializers import EventFullNoteSerializer
from event.models import Event, Involved


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
    ClickHistoryMixin, MassiveEdit, viewsets.ModelViewSet):
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

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': EventFullNoteSerializer,
            'create': EventMediumSerializer,
            'update': EventMediumSerializer,
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


class InvolvedViewSet(MassiveEdit, BaseGenericViewSet):
    queryset = Involved.objects.all()
    serializer_class = InvolvedSerializer
    search_fields = []

