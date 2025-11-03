from django.db.models import Count
from rest_framework import viewsets, permissions
from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.views.common_views import BaseStatusViewSet, MassiveEdit
from api.permissions import IsAdminOrReadOnly, IsEditorOrCreateOrRead
from api.views.catalogs.event_serializers import (
    EventGroupSerializer, EventTypeFullSerializer, EventTypeSerializer,
    PurposeSerializer)
from event.models import EventGroup, EventType, Purpose


class EventGroupViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [IsAdminOrReadOnly]
    queryset = EventGroup.objects.all()
    serializer_class = EventGroupSerializer


class EventTypeViewSet(MassiveEdit, BaseStatusViewSet):
    permission_classes = [IsEditorOrCreateOrRead]
    queryset = EventType.objects.all()\
        .annotate(count=Count('events'))\
        .distinct()
    serializer_class = EventTypeFullSerializer
    filterset_fields = ['status_validation', 'event_group']
    ordering_fields = ['__auto__']

    def get_serializer_class(self):
        action_serializer = {
            'list': EventTypeSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class PurposeViewSet(BaseStatusViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Purpose.objects.all()\
        .annotate(events_count=Count('events'))\
        .distinct()
    serializer_class = PurposeSerializer
    filterset_fields = []
