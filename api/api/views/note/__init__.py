from django_filters import FilterSet, DateFilter, CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins, permissions
from rest_framework.viewsets import GenericViewSet

from api.views.action_file import ActionFileMixin
from source.models import Note, NoteFile

from api.pagination import CustomPagination
from api.views.note.serializers import (
    NoteSerializer, NoteCreateSerializer, NoteFullSerializer,
    NoteFileSerializer, MentionSerializer)
from api.views.common_views import UnaccentSearchFilter, OrderingAutoFilter


class NoteFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    status_register = CharFilter(field_name='status_register__name')

    class Meta:
        model = Note
        fields = {
            'source': ['exact']
        }


class NoteViewSet(ActionFileMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
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

    pagination_class = CustomPagination

    filterset_class = NoteFilter

    # filter_backends = [
    #     OrderingFilter, DjangoFilterBackend, UnaccentSearchFilter]
    filter_backends = [
        OrderingAutoFilter, DjangoFilterBackend, UnaccentSearchFilter]
    # SearchFilter
    search_fields = ["title", "=nota_id_ref"]
    # ordering_fields = ['id', 'date', 'status_register__order']
    ordering_fields = ['__auto__']
    ordering = ['id']
    serializer_class = NoteSerializer
    action_add_file_param = 'note'

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': NoteFullSerializer,
            'create': NoteFullSerializer,
            # 'update': NoteCreateSerializer,
            'update': NoteFullSerializer,
            'add_file': NoteFileSerializer,
            # 'patch': NoteCreateSerializer,

        }
        return action_serializer.get(self.action, self.serializer_class)


class NoteFileViewSet(mixins.DestroyModelMixin, GenericViewSet):
    queryset = NoteFile.objects.all()
    serializer_class = NoteFileSerializer


