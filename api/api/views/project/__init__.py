from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from actor.models import Actor
from api.pagination import CustomPagination
from api.views.action_export_xls import ExportXlsMixin
from api.views.action_file import ActionFileMixin
from api.views.actor.serializers import ActorFullCountSerializer
from api.views.common_views import UnaccentSearchFilter, BaseStatusViewSet
from api.views.note.serializers import ProjectSemiFullSerializer
from project.models import Conflict, Project, ProjectFile

from .list_serializers import (
    ConflictSerializer, ProjectBasicSerializer, ConflictFullSerializer,
    ProjectExportSerializer)
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


class ProjectViewSet(ActionFileMixin, ExportXlsMixin, viewsets.ModelViewSet):
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
    xls_attrs = [
        {
            "name": "ID",
            "width": 8,
            "field": "id"

        },
        {
            "name": "Nombre",
            "width": 40,
            "field": "name"
        },
        {
            "name": "Nombres alternativos",
            "width": 40,
            "field": "alternative_name"
        },
        {
            "name": "Descripción",
            "width": 40,
            "field": "description"
        },
        {
            "name": "ID antiguo",
            "width": 8,
            "field": "proyecto_id_ref"
        },
        {
            "name": "ID de conflicto",
            "width": 8,
            "field": "conflict__id"
        },
        {
            "name": "Nombre de conflicto",
            "width": 40,
            "field": "conflict__name"
        },
        {
            "name": "Descripción de conflicto",
            "width": 40,
            "field": "conflict__description"
        },
        {
            "name": "Tipo de megaproyecto",
            "width": 40,
            "field": "megaproject_type__name"
        },
        {
            "name": "Tipos de extractivismo",
            "width": 40,
            "field": "megaproject_type__extractivism_types"
        },
        {
            "name": "ID de proyecto agrupador",
            "width": 8,
            "field": "parent_project__id"
        },
        {
            "name": "Nombre de proyecto agrupador",
            "width": 40,
            "field": "parent_project__name"
        },
        {
            "name": "ID de ubicación principal",
            "width": 8,
            "field": "locations__id"
        },
        {
            "name": "ID de Entidad",
            "width": 8,
            "field": "locations__state__inegi_code"
        },
        {
            "name": "Entidad",
            "width": 40,
            "field": "locations__state__name"
        },
        {
            "name": "ID de Municipio",
            "width": 8,
            "field": "locations__municipality__inegi_code"
        },
        {
            "name": "Municipio",
            "width": 40,
            "field": "locations__municipality__name"
        },
        {
            "name": "ID de Localidad",
            "width": 8,
            "field": "locations__locality__inegi_code"
        },
        {
            "name": "Localidad",
            "width": 40,
            "field": "locations__locality__name"
        },
        {
            "name": "Latitud",
            "width": 20,
            "field": "locations__latitude"
        },
        {
            "name": "Longitud",
            "width": 20,
            "field": "locations__longitude"
        }
    ]
    xls_name = "Proyectos"
    permission_classes = [permissions.AllowAny]

    pagination_class = CustomPagination

    filterset_class = ProjectFilter

    # filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_backends = [
        UnaccentSearchFilter, OrderingFilter, DjangoFilterBackend]
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
            queryset = queryset.prefetch_related("others_parents")
        return queryset

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ProjectFullSerializer,
            'create': ProjectSemiFullSerializer,
            # 'update': ProjectEditSerializer,
            'update': ProjectFullSerializer,
            'add_file': ProjectFileSerializer,
            'export_xls': ProjectExportSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_query_for_export_xls(self):
        from space_time.models import Location
        from django.db.models import OuterRef, Subquery

        max_priority_location = Location.objects.filter(
            project=OuterRef('id')
        ).order_by('-status_location__priority')

        # TODO: Ricardo el annotate es para traer en una sola peticion los datos
        # de location y sus relacionados sin sobrecargar el prefetch_related
        # revisar si se puede subir a global los select_related

        queryset = self.get_queryset()\
            .select_related("megaproject_type", "parent_project")\
            .annotate(
                locations__id=Subquery(max_priority_location.values('id')[:1]),
                locations__state__inegi_code=Subquery(
                    max_priority_location.values('state__inegi_code')[:1]),
                locations__state__name=Subquery(
                    max_priority_location.values('state__name')[:1]),
                locations__municipality__inegi_code=Subquery(
                    max_priority_location.values('municipality__inegi_code')[:1]),
                locations__municipality__name=Subquery(
                    max_priority_location.values('municipality__name')[:1]),
                locations__locality__inegi_code=Subquery(
                    max_priority_location.values('locality__inegi_code')[:1]),
                locations__locality__name=Subquery(
                    max_priority_location.values('locality__name')[:1]),
                locations__latitude=Subquery(
                    max_priority_location.values('latitude')[:1]),
                locations__longitude=Subquery(
                    max_priority_location.values('longitude')[:1]),
        )
        return self.filter_queryset(queryset)

    @action(detail=True, methods=['get'])
    def related_actors(self, request, pk=None):
        from django.db.models import Count
        project = self.get_object()
        actors = Actor.objects\
            .filter(participants__mention__project=project)\
            .annotate(participant_count=Count('participants'))\
            .distinct()

        actor_full = ActorFullCountSerializer(
            actors, many=True, context={'project': project}).data

        sorted_actors = sorted(
            actor_full, key=lambda x: x['participant_count'], reverse=True)

        return Response(sorted_actors)


class ProjectFileViewSet(mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]


class ConflictViewSet(BaseStatusViewSet):
    queryset = Conflict.objects.all()\
        .prefetch_related("projects")
    serializer_class = ConflictFullSerializer

    def get_serializer_class(self):
        action_serializer = {
            'list': ConflictSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
