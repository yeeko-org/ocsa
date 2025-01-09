from django.db.models import Count
from rest_framework import viewsets, permissions
from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.views.common_views import BaseStatusViewSet, UnaccentSearchFilter

from api.views.catalogs import EventGroupSerializer, EventTypeFullSerializer, EventTypeSerializer, \
    EventSubtypeFullSerializer, EventSubtypeSerializer
from event.models import EventGroup, EventType, EventSubtype


class EventGroupViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = EventGroup.objects.all()
    serializer_class = EventGroupSerializer


class EventTypeViewSet(BaseStatusViewSet):
    queryset = EventType.objects.all()\
        .prefetch_related('event_subtypes')\
        .annotate(count=Count('events'))\
        .distinct()
    serializer_class = EventTypeFullSerializer
    filterset_fields = ['status_validation', 'event_group']

    def get_serializer_class(self):
        action_serializer = {
            'list': EventTypeSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class EventSubtypeFilter(FilterSet):
    event_group = NumberFilter(
        field_name='event_types__event_group', lookup_expr='exact')
    event_type = NumberFilter(
        field_name='event_types', lookup_expr='exact')

    class Meta:
        model = EventSubtype
        fields = {
            'status_validation': ['exact']
        }


class EventSubtypeViewSet(BaseStatusViewSet):
    queryset = EventSubtype.objects.all()\
        .prefetch_related('events')\
        .annotate(count=Count('events'))\
        .distinct()
    serializer_class = EventSubtypeFullSerializer
    filterset_class = EventSubtypeFilter

    def get_serializer_class(self):
        action_serializer = {
            'list': EventSubtypeSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
