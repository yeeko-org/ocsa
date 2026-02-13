from django_filters import FilterSet, DateFilter, CharFilter, BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from api.permissions import (
    IsAuthenticatedOrReadOnly, ByStatusOrReadOnly)
from api.views.action_file import ActionFileMixin
from source.models import Note, NoteFile

from api.pagination import CustomPagination
from api.views.note.serializers import (
    NoteSerializer, NoteCreateSerializer, NoteFullSerializer,
    NoteFileSerializer, MentionSerializer, PreMentionSerializer)
from api.views.common_views import (
    UnaccentSearchFilter, OrderingAutoFilter, ClickHistoryMixin)


class NoteFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    has_files = BooleanFilter(
        field_name='files', lookup_expr='isnull', exclude=True)
    editor = CharFilter(method='filter_by_user')
    status_register = CharFilter(field_name='status_register__name')
    reviewer = CharFilter(method='filter_by_user')

    def filter_by_user(self, queryset, name, value):
        if not value:
            return queryset
        if name == 'editor':
            return queryset.filter(editors__id=value)
        elif name == 'reviewer':
            return queryset.filter(reviewers__id=value)
        return queryset

    class Meta:
        model = Note
        fields = {
            'source': ['exact'],
            # 'editors': ['exact'],
            # 'reviewers': ['exact'],
        }


class NoteViewSet(ClickHistoryMixin, ActionFileMixin, viewsets.ModelViewSet):
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
    click_actions = ['opened', 'updated']
    serializer_class = NoteSerializer
    action_add_file_param = 'note'

    def get_queryset(self):
        # is_retrieve = self.action == 'retrieve'
        is_full = self.action in [
            'retrieve', 'update', 'partial_update', 'create']
        queryset = super().get_queryset()
        queryset = self.queryset.prefetch_related(
            'files',
            'mentions__project__locations',
            'mentions__project__locations__municipality',
            'mentions__project__locations__locality',
            'mentions__project__conflict',
            'mentions__project__parent_project',
            'mentions__events__involvements',
            'mentions__events__locations',
            'mentions__status_history',
            'articles',
        ) if is_full else queryset
        return queryset

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': NoteFullSerializer,
            'create': NoteFullSerializer,
            # 'update': NoteCreateSerializer,
            'update': NoteFullSerializer,
            'add_file': NoteFileSerializer,
            'start_pre_capture': NoteFullSerializer,
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
        self.save_click_action(request, instance, 'updated')
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

    @action(detail=True, methods=['post'])
    def start_pre_capture(self, request, pk=None):
        from source.criteria.pre_capture import PreCaptureManager
        note = self.get_object()
        if note.frozen_pre_capture:
            return Response(
                {'detail': 'Pre-capture is already frozen for this note.'},
                status=400)
        manager = PreCaptureManager(ai_engine="gemini-3-flash-preview")
        manager.build_direct_criteria(note.articles.first())
        note_saved = Note.objects.get(pk=note.id)
        serializer = self.get_serializer(
            note_saved, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def edit_pre_capture(self, request, pk=None):
        note = self.get_object()
        # validar con PreMentionSerializer
        req_data = request.data
        validator = PreMentionSerializer(data=req_data)
        if not validator.is_valid():
            return Response(validator.errors, status=400)
        # path = request.data.get('path', '')
        # discarded = request.data.get('discarded', False)
        data = validator.validated_data
        path = data.get('path', '')
        discarded = data.get('discarded')
        element_id = data.get('element_id', None)
        new_content = note.set_pre_capture(
            path=path,
            discarded=discarded,
            element_id=element_id)
        return Response({'content': new_content})

    @action(detail=True, methods=['post'])
    def pre_capture_by_path(self, request, pk=None):
        note = self.get_object()

        req_data = request.data
        path = req_data.get('path', '')
        if not path:
            return Response({'detail': 'Path is required.'}, status=400)
        # path = request.data.get('path', '')
        # discarded = request.data.get('discarded', False)

        new_content = note.get_first_match(path=path)
        return Response({'content': new_content})


class NoteFileViewSet(mixins.DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = NoteFile.objects.all()
    serializer_class = NoteFileSerializer

