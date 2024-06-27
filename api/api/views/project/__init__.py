from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend

from api.pagination import CustomPagination
from project.models import Project
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .create_serializers import ProjectCreateSerializer, ProjectEditSerializer
from .list_serializers import ProjectBasicSerializer
from .retrieve_serializers import ProjectFullSerializer


class ProjectFilter(FilterSet):
    state = NumberFilter(
        field_name='locations__location__state', lookup_expr='exact')
    social_impact = NumberFilter(
        field_name='mentions__impacts__impact_type', lookup_expr='exact')
    social_subimpact = NumberFilter(
        field_name='mentions__impacts__impact_subtype', lookup_expr='exact')
    event_type = NumberFilter(
        field_name='mentions__events__event_type', lookup_expr='exact')
    event_subtype = NumberFilter(
        field_name='mentions__events__event_subtype', lookup_expr='exact')

    class Meta:
        model = Project
        fields = {
            'status_register': ['exact'],
            'megaproject_type': ['exact'],
            'scale': ['exact'],
            'status_project': ['exact'],
        }


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().select_related(
        "parent_project",
        "conflict",
        "megaproject_type",
        "scale",
        "status_project",
        "status_register",
    ).prefetch_related(
        "mentions",
        "mentions__note",
        "mentions__impacts",
        "mentions__participants",
        "mentions__participants__actor",
    )
    permission_classes = [permissions.IsAuthenticated]

    pagination_class = CustomPagination

    filterset_class = ProjectFilter

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "official_name",
        "common_name",
        # "description"
    ]
    ordering_fields = ['id', 'official_name']
    ordering = ['id']

    serializer_class = ProjectBasicSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ProjectFullSerializer,
            'create': ProjectCreateSerializer,
            'update': ProjectEditSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
