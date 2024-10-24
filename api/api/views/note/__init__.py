from django_filters import FilterSet, DateFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from source.models import Note

from api.pagination import CustomPagination
from api.views.note.serializers import (
    NoteSerializer, NoteCreateSerializer, NoteFullSerializer)


class NoteFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Note
        fields = {
            'source': ['exact']
        }


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()\
        .prefetch_related(
            'mentions',
            'mentions__project',
            'mentions__impacts',
            'mentions__participants',
            'mentions__participants__actor',
            'mentions__participants__interests',
            'mentions__events',
            'mentions__events__involvements',
        )
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    pagination_class = CustomPagination

    filterset_class = NoteFilter

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "title",
    ]
    ordering_fields = ['id', 'date']
    ordering = ['id']

    serializer_class = NoteSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': NoteFullSerializer,
            'create': NoteCreateSerializer,
            'update': NoteCreateSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
