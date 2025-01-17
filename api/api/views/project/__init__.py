from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from actor.models import Actor
from api.merge_mix import MergeSerializerMixin
from api.pagination import CustomPagination
from api.views.action_file import ActionFileMixin
from api.views.actor.serializers import ActorFullCountSerializer
from api.views.common_views import UnaccentSearchFilter
from api.views.note.serializers import ProjectSemiFullSerializer
from project.models import Conflict, Project, ProjectFile
from source.models import Mention
from space_time.models import Location

from .list_serializers import ConflictSerializer, ProjectBasicSerializer
from .retrieve_serializers import ProjectFileSerializer, ProjectFullSerializer


class ProjectFilter(FilterSet):
    state = NumberFilter(
        field_name='locations__state', lookup_expr='exact')
    impact_type = NumberFilter(
        field_name='mentions__impacts__impact_type', lookup_expr='exact')
    impact_subtype = NumberFilter(
        field_name='mentions__impacts__impact_subtype', lookup_expr='exact')
    event_type = NumberFilter(
        field_name='mentions__events__event_type', lookup_expr='exact')
    event_subtype = NumberFilter(
        field_name='mentions__events__event_subtype', lookup_expr='exact')
    extractivism_type = NumberFilter(
        field_name='megaproject_type__extractivism_types',
        lookup_expr='exact')

    class Meta:
        model = Project
        fields = {
            'status_validation': ['exact'],
            'megaproject_type': ['exact'],
            'status_project': ['exact'],
            'is_grouper': ['exact'],
        }


class ProjectViewSet(ActionFileMixin, MergeSerializerMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all().select_related(
        "parent_project",
        "conflict",
    ).prefetch_related(
        "locations",
        "children_projects",
        "mentions",
        "mentions__note",
        "mentions__impacts",
        "mentions__participants",
        "mentions__participants__actor",
    ).distinct()
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    pagination_class = CustomPagination

    filterset_class = ProjectFilter

    # filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_backends = [UnaccentSearchFilter,
                       OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "alternative_name",
        "=proyecto_id_ref",
        # "description"
    ]
    ordering_fields = [
        'id', 'name', 'status_validation__order', 'status_location__order']
    ordering = ['id']

    serializer_class = ProjectBasicSerializer

    action_add_file_param = "project"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset\
                .prefetch_related("others_parents")
        return queryset

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ProjectFullSerializer,
            'create': ProjectSemiFullSerializer,
            # 'update': ProjectEditSerializer,
            'update': ProjectFullSerializer,
            'add_file': ProjectFileSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_from_obj(self, from_id):
        return Project.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Location.objects.filter(project=from_obj)\
            .update(project=to_obj)
        Mention.objects.filter(project=from_obj)\
            .update(project=to_obj)

    @action(detail=True, methods=['get'])
    def actors(self, request, pk=None):
        project = self.get_object()
        actors = Actor.objects.filter(
            participants__mention__project=project
        ).distinct()

        return Response(ActorFullCountSerializer(actors, many=True).data)


class ProjectFileViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]


class ConflictViewSet(viewsets.ModelViewSet):
    queryset = Conflict.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name']
    ordering = ['id']
    serializer_class = ConflictSerializer
