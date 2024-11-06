from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import GenericViewSet

from api.merge_mix import MergeSerializerMixin
from api.pagination import CustomPagination
from api.views.action_file import ActionFileMixin
from project.models import Project, ProjectFile, ProjectLocation
from source.models import Mention
from .create_serializers import ProjectCreateSerializer, ProjectEditSerializer
from .list_serializers import ProjectBasicSerializer
from .retrieve_serializers import ProjectFileSerializer, ProjectFullSerializer


class ProjectFilter(FilterSet):
    state = NumberFilter(
        field_name='locations__location__state', lookup_expr='exact')
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
        }


class ProjectViewSet(ActionFileMixin, MergeSerializerMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all().select_related(
        "parent_project",
        "conflict",
    ).prefetch_related(
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

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "common_name",
        # "description"
    ]
    ordering_fields = [
        'id', 'name', 'status_validation__order', 'status_location__order']
    ordering = ['id']

    serializer_class = ProjectBasicSerializer

    action_add_file_param = "project"

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ProjectFullSerializer,
            'create': ProjectCreateSerializer,
            'update': ProjectEditSerializer,
            'add_file': ProjectFileSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_from_obj(self, from_id):
        return Project.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        ProjectLocation.objects.filter(project=from_obj)\
            .update(project=to_obj)
        Mention.objects.filter(project=from_obj)\
            .update(project=to_obj)


class ProjectFileViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]