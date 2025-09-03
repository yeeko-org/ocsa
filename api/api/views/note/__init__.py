from django_filters import FilterSet, DateFilter, CharFilter, BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from api.permissions import (
    IsAuthenticatedOrReadOnly, ByStatusOrReadOnly)
from api.views.action_file import ActionFileMixin
from source.models import Note, NoteFile

from api.pagination import CustomPagination
from api.views.note.serializers import (
    NoteSerializer, NoteCreateSerializer, NoteFullSerializer,
    NoteFileSerializer, MentionSerializer)
from api.views.common_views import (
    UnaccentSearchFilter, OrderingAutoFilter)


class NoteFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    status_register = CharFilter(field_name='status_register__name')
    has_files = BooleanFilter(
        field_name='files', lookup_expr='isnull', exclude=True)

    class Meta:
        model = Note
        fields = {
            'source': ['exact'],
            'editors': ['exact'],
            'reviewers': ['exact'],
        }


class NoteViewSet(ActionFileMixin, viewsets.ModelViewSet):
    permission_classes = [ByStatusOrReadOnly]
    queryset = Note.objects.all()\
        .prefetch_related(
            'mentions',
            'mentions__project',
            'mentions__impacts',
            'mentions__participants',
            'mentions__participants__actor',
            'mentions__participants__interests',
            'mentions__events',
    )

    pagination_class = CustomPagination

    filterset_class = NoteFilter

    filter_backends = [
        OrderingAutoFilter, DjangoFilterBackend, UnaccentSearchFilter]
    # SearchFilter
    search_fields = ["title", "=nota_id_ref"]
    # ordering_fields = ['id', 'date', 'status_register__order']
    ordering_fields = ['__auto__']
    ordering = ['id']
    serializer_class = NoteSerializer
    action_add_file_param = 'note'

    def get_queryset(self):
        is_retrieve = self.action == 'retrieve'
        queryset = super().get_queryset()
        queryset = self.queryset.prefetch_related(
            'files',
            'mentions__project__locations',
            'mentions__project__conflict',
            'mentions__project__parent_project',
            'mentions__events__involvements',
            'mentions__events__locations',
            'mentions__status_history',
            'articles',
        ) if is_retrieve else queryset
        return queryset

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

    def create(self, request, *args, **kwargs):
        data = request.data
        # data['editor'] = request.user.id
        data['editors'] = [request.user.id]
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = serializer_class(
            instance, data=request.data, partial=partial,
            context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            note_saved = serializer.instance
            if request.user.is_staff:
                note_saved.reviewers.add(request.user)
            else:
                note_saved.editors.add(request.user)
            new_serializer = NoteFullSerializer(
                note_saved, context=self.get_serializer_context())
            return Response(new_serializer.data)

        return Response(serializer.errors, status=400)


class NoteFileViewSet(mixins.DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = NoteFile.objects.all()
    serializer_class = NoteFileSerializer

