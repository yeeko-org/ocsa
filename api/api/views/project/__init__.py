from django_filters import FilterSet, NumberFilter, BooleanFilter, CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.views.confirm_delete import CustomDeleteMixin

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.permissions import DynamicCatalogPermission
from actor.models import Actor
from api.pagination import CustomPagination
from api.views.action_file import ActionFileMixin
from api.views.actor.serializers import ActorFullCountSerializer
from api.views.common_views import (
    UnaccentSearchFilter, BaseStatusViewSet, MassiveEdit, ClickHistoryMixin)
# from api.views.note.serializers import LocationVizSerializer
from api.views.note.serializers import ProjectSemiFullSerializer
from project.models import Conflict, Project, ProjectFile

from .list_serializers import (
    ConflictSerializer, ProjectBasicSerializer, ConflictFullSerializer,
    ProjectMiniBasicSerializer, LocationVizSerializer)
from .retrieve_serializers import ProjectFileSerializer, ProjectFullSerializer


class ProjectFilter(FilterSet):
    state = NumberFilter(
        field_name='locations__state', lookup_expr='exact')
    impact_group = NumberFilter(
        field_name='mentions__impacts__impact_type__impact_group',
        lookup_expr='exact')
    impact_type = NumberFilter(
        field_name='mentions__impacts__impact_type', lookup_expr='exact')
    impact_subtype = NumberFilter(
        field_name='mentions__impacts__impact_subtype', lookup_expr='exact')
    event_type = NumberFilter(
        field_name='mentions__events__event_type', lookup_expr='exact')
    # extractivism_type = NumberFilter(
    #     field_name='megaproject_type__extractivism_types',
    #     lookup_expr='exact')
    conflict_criteria = BooleanFilter(method='custom_conflict_criteria')
    has_conflict = BooleanFilter(
        field_name='conflict', lookup_expr='isnull', exclude=True)
    extractivism_type = CharFilter(method='filter_extractivism_type')
    has_locations = BooleanFilter(
        field_name='locations', lookup_expr='isnull', exclude=True)

    def filter_extractivism_type(self, queryset, name, value):
        # print("Filtering by extractivism_type:", value)
        if value == 0:
            return queryset.filter(
                megaproject_type__extractivism_types__isnull=True)
        return queryset.filter(megaproject_type__extractivism_types=value)

    def custom_conflict_criteria(self, queryset, name, value):
        from django.db.models import Q
        print(f"Name: {name}, Value: {value}")
        if value:
            return queryset.filter(
                Q(mentions__events__event_type__event_group__id=1)
                | Q(mentions__impacts__isnull=False),
                mentions__events__event_type__event_group__id=2
            )
        else:
            return queryset.exclude(
                Q(mentions__events__event_type__event_group__id=1)
                | Q(mentions__impacts__isnull=False),
                mentions__events__event_type__event_group__id=2
            )


    class Meta:
        model = Project
        fields = {
            'status_validation': ['exact'],
            'status_location': ['exact'],
            'megaproject_type': ['exact'],
            'status_project': ['exact'],
            'is_grouper': ['exact'],
        }


class ProjectViewSetMixin(viewsets.ModelViewSet):
    permission_classes = [DynamicCatalogPermission]
    pagination_class = CustomPagination
    filterset_class = ProjectFilter
    filter_backends = [
        UnaccentSearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "alternative_name",
        "=proyecto_id_ref"
    ]
    ordering_fields = [
        'id', 'name', 'status_validation__order', 'status_location__order']
    ordering = ['id']


class ProjectViewSet(
        ClickHistoryMixin, CustomDeleteMixin, ActionFileMixin, MassiveEdit,
        ProjectViewSetMixin):
    queryset = Project.objects.all().select_related(
        "parent_project",
        "conflict",
    ).prefetch_related(
        "locations",
        "children_projects",
        "mentions",
        "mentions__note",
        "mentions__events",
        "mentions__impacts",
        "mentions__participants",
        "mentions__participants__interests",
        "mentions__participants__actor",
        "mentions__participants__actor__belongs",
    ).distinct()
    # add_locations = True
    click_actions = ['opened', 'created', 'saved']

    pagination_class = CustomPagination
    serializer_class = ProjectBasicSerializer
    filterset_class = ProjectFilter

    # filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_backends = [
        UnaccentSearchFilter, OrderingFilter, DjangoFilterBackend]


    action_add_file_param = "project"

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ProjectFullSerializer,
            'create': ProjectSemiFullSerializer,
            # 'update': ProjectEditSerializer,
            'update': ProjectFullSerializer,
            'add_file': ProjectFileSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_queryset(self):
        queryset = super().get_queryset()
        is_logged_in = self.request.user.is_authenticated
        if not is_logged_in:
            queryset = queryset.filter(status_validation__is_public=True)

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related("others_parents")
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['editors'] = [request.user.id]
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        project_saved = serializer.instance
        project_saved.editors.add(request.user)
        new_serializer = self.get_serializer(project_saved)
        return Response(new_serializer.data)

    @action(detail=True, methods=['get'])
    def related_actors(self, request, pk=None):
        from django.db.models import Count
        project = self.get_object()
        actors = Actor.objects\
            .filter(participants__mention__project=project)\
            .annotate(participant_count=Count('participants'))\
            .distinct()

        query_params = request.query_params
        if participant_group := query_params.get('participant_group', None):
            actors = actors.filter(
                participants__participant_types__participant_group=participant_group
            )

        actor_full = ActorFullCountSerializer(
            actors, many=True, context={'project': project}).data

        sorted_actors = sorted(
            actor_full, key=lambda x: x['participant_count'], reverse=True)

        return Response(sorted_actors)


class ProjectFileViewSet(
    mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]


class ProjectMiniViewSet(ProjectViewSetMixin):
    queryset = Project.objects.all().select_related(
        "parent_project",
    ).prefetch_related(
        "locations",
    ).distinct()
    serializer_class = ProjectMiniBasicSerializer


class ConflictFilter(FilterSet):
    state = NumberFilter(
        field_name='projects__locations__state', lookup_expr='exact')
    has_projects = BooleanFilter(
        field_name='projects', lookup_expr='isnull', exclude=True)
    extractivism_type = NumberFilter(
        field_name='projects__megaproject_type__extractivism_types',
        lookup_expr='exact')
    megaproject_type = NumberFilter(
        field_name='projects__megaproject_type', lookup_expr='exact')

    class Meta:
        model = Conflict
        fields = {
            'status_validation': ['exact'],
        }

class ConflictViewSet(BaseStatusViewSet):
    queryset = Conflict.objects.all()\
        .prefetch_related("projects")
    serializer_class = ConflictFullSerializer
    filterset_class = ConflictFilter
    search_fields = ['name', 'projects__name']

    def get_serializer_class(self):
        action_serializer = {
            'list': ConflictSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
