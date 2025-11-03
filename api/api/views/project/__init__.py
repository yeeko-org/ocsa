from django_filters import FilterSet, NumberFilter, BooleanFilter, CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from api.views.confirm_delete import CustomDeleteMixin

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.permissions import DynamicCatalogPermission, LocationPermission
from actor.models import Actor
from space_time.models import Location
from api.pagination import CustomPagination
from api.views.action_export_xls import ExportXlsMixin
from api.views.action_file import ActionFileMixin
from api.views.actor.serializers import ActorFullCountSerializer
from api.views.common_views import (
    UnaccentSearchFilter, BaseStatusViewSet, MassiveEdit)
from api.views.note.serializers import LocationVizSerializer
from project.models import Conflict, Project, ProjectFile

from .list_serializers import (
    ConflictSerializer, ProjectBasicSerializer, ConflictFullSerializer,
    ProjectExportSerializer, ProjectMiniBasicSerializer, MentionSerializer)
from .retrieve_serializers import ProjectFileSerializer, ProjectFullSerializer
from api.views.note.serializers import ProjectSemiFullSerializer


class ProjectFilter(FilterSet):
    state = NumberFilter(
        field_name='locations__state', lookup_expr='exact')
    impact_type = NumberFilter(
        field_name='mentions__impacts__impact_type', lookup_expr='exact')
    impact_subtype = NumberFilter(
        field_name='mentions__impacts__impact_subtype', lookup_expr='exact')
    event_type = NumberFilter(
        field_name='mentions__events__event_type', lookup_expr='exact')
    # extractivism_type = NumberFilter(
    #     field_name='megaproject_type__extractivism_types',
    #     lookup_expr='exact')
    extractivism_type = CharFilter(method='filter_extractivism_type')
    has_locations = BooleanFilter(
        field_name='locations', lookup_expr='isnull', exclude=True)

    def filter_extractivism_type(self, queryset, name, value):
        print("Filtering by extractivism_type:", value)
        if value == 0:
            return queryset.filter(
                megaproject_type__extractivism_types__isnull=True)
        return queryset.filter(megaproject_type__extractivism_types=value)

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
        CustomDeleteMixin, ActionFileMixin, MassiveEdit, ExportXlsMixin,
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
    add_locations = True

    xls_attrs = [
        {
            "name": "ID",
            "width": 5,
            "field": "id"
        },
        {
            "name": "ID antiguo",
            "width": 5,
            "field": "proyecto_id_ref"
        },
        {
            "name": "Nombre",
            "width": 35,
            "field": "name"
        },
        {
            "name": "Nombres alternativos",
            "width": 25,
            "field": "alternative_name"
        },
        {
            "name": "Descripción",
            "width": 40,
            "field": "description"
        },
        {
            "name": "Es agrupador",
            "width": 8,
            "field": "is_grouper"
        },
        {
            "name": "ID de conflicto",
            "width": 5,
            "field": "conflict__id"
        },
        {
            "name": "Nombre de conflicto",
            "width": 40,
            "field": "conflict__name"
        },
        {
            "name": "Descripción de conflicto",
            "width": 25,
            "field": "conflict__description"
        },
        {
            "name": "Tipo de megaproyecto",
            "width": 20,
            "field": "megaproject_type__name"
        },
        {
            "name": "Tipos de extractivismo",
            "width": 25,
            "field": "extractivism_types"
        },
        {
            "name": "ID de proyecto agrupador",
            "width": 5,
            "field": "parent_project__id"
        },
        {
            "name": "Nombre de proyecto agrupador",
            "width": 30,
            "field": "parent_project__name"
        }
    ]
    xls_name = "Exportación de Proyectos"

    pagination_class = CustomPagination
    filterset_class = ProjectFilter

    # filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_backends = [
        UnaccentSearchFilter, OrderingFilter, DjangoFilterBackend]

    serializer_class = ProjectBasicSerializer

    action_add_file_param = "project"

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status_validation__is_public=True)

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related("others_parents")
        elif self.action == "export_xls":
            queryset = Project.objects.all().select_related(
                "parent_project",
                "conflict",
                "megaproject_type",
            ).prefetch_related(
                "megaproject_type__extractivism_types"
            ).distinct()
        return queryset

    # def list(self, request, *args, **kwargs):
    #     response = super().list(request, *args, **kwargs)
    #     # print("ProjectViewSet.list, response: ", response.data)
    #     projects_ids = [item['id'] for item in response.data['results']]
    #     mentions = Mention.objects\
    #         .filter(project_id__in=projects_ids)\
    #         .select_related('note')\
    #         .prefetch_related(
    #             'events',
    #             'impacts',
    #             # 'participants',
    #             # 'participants__actor',
    #             # 'participants__interests',
    #         )
    #     mentions_serialized = MentionSerializer(mentions, many=True).data
    #     # response.data["aaa"] = "bbb"
    #     response.data["mentions"] = mentions_serialized
    #     return response

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
        annotations = self.get_annotations('project')
        queryset = self.get_queryset() \
            .annotate(**annotations)\
            .select_related(
                'parent_project', 'conflict', 'megaproject_type'
            )\
            .prefetch_related("megaproject_type__extractivism_types")\
            .distinct()
        return self.filter_queryset(queryset)

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


class ProjectMiniViewSet(ProjectViewSetMixin):
    queryset = Project.objects.all().select_related(
        "parent_project",
    ).prefetch_related(
        "locations",
    ).distinct()
    serializer_class = ProjectMiniBasicSerializer


class ProjectLocationFilter(FilterSet):
    extractivism_type = NumberFilter(
        field_name='project__megaproject_type__extractivism_types',
        lookup_expr='exact')

    class Meta:
        model = Location
        fields = ["state", "type_location"]


class ProjectLocationViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [LocationPermission]

    queryset = Location.objects.all()
        # .filter(project__isnull=False)\
        # .select_related("project")
        # .select_related("project", "project__megaproject_type")

    # queryset = Project.objects.all().prefetch_related("locations").distinct()
    serializer_class = LocationVizSerializer
    filter_backends = [
        UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['state__name',
                     'municipality__name',
                     'locality__name',
                     'project__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(
                status_location__is_public=True, project__isnull=False)\
                .select_related("project")
        else:
            # TODO: Algún día lo quitaremos
            queryset = queryset.filter(
                status_location__is_public=True, project__isnull=False)\
                .select_related("project")
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        location_points = queryset.filter(
            type_location='point', latitude__isnull=False,
            longitude__isnull=False) \
            .select_related("project")
        other_locations = queryset.\
            filter(geojson__isnull=False)\
            .exclude(type_location='point')\
            .select_related("project")
        features = []
        no_geojson = 0

        # all_locations = location_points | other_locations
        # serializer = self.get_serializer(all_locations, many=True)
        # for location in serializer.data:
        #     location_data = location.copy()
        #     project = location_data.get('project')
        #     if not project:
        #         print("No project found for location:", location)
        #         continue
        #     geojson = location_data.pop('geojson', None)
        #     if geojson is not None:
        #         if my_features := geojson.get('features'):
        #             geojson = my_features[0].get('geometry')
        #
        #     if not geojson and location.get('type_location') == 'point':
        #         latitude = location.get('latitude')
        #         longitude = location.get('longitude')
        #         if latitude is not None and longitude is not None:
        #             geojson = {
        #                 "type": "Point",
        #                 "coordinates": [longitude, latitude]
        #             }
        #
        #     if not geojson:
        #         # print("No geojson found for location:", location)
        #         no_geojson += 1
        #         continue
        #
        #     feature = {
        #         "type": "Feature",
        #         "geometry": geojson,
        #         "properties": location_data,
        #     }
        #     features.append(feature)

        # return Response(serializer.data)
        keep_fields = [
            "id", "state", "municipality", "locality", "project"]

        serializer_points = self.get_serializer(location_points, many=True)
        for loc_point in serializer_points.data:
            latitude = loc_point.get('latitude', None)
            longitude = loc_point.get('longitude', None)
            if latitude is None or longitude is None:
                continue
            latitude = int(latitude * 100000) / 100000
            longitude = int(longitude * 100000) / 100000
            properties = {}
            for key in keep_fields:
                properties[key] = loc_point.get(key)
            geojson = {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }

            feature = {
                "type": "Feature",
                "geometry": geojson,
                "properties": properties,
            }
            features.append(feature)

        serializer_other = self.get_serializer(other_locations, many=True)
        extra_large_locations = []
        for loc_data in serializer_other.data:
            geojson = loc_data.get('geojson', None)
            if my_features := geojson.get('features'):
                new_geojson = my_features[0].get('geometry').copy()
                coordinates = new_geojson.get('coordinates', [])
                if len(coordinates) > 100:
                    extra_large_locations.append(loc_data)
                new_coordinates = []
                for coord_set in coordinates:
                    new_coord_set = []
                    for coord in coord_set:
                        if isinstance(coord, list):
                            new_sub_coord = []
                            for sub_coord in coord:
                                new_sub_coord.append(
                                    int(sub_coord * 100000) / 100000)
                            new_coord_set.append(new_sub_coord)
                        else:
                            new_coord_set.append(int(coord * 100000) / 100000)

                    new_coordinates.append(new_coord_set)
                new_geojson['coordinates'] = new_coordinates

            else:
                continue

            properties = {}
            for key in keep_fields:
                properties[key] = loc_data.get(key)

            feature = {
                "type": "Feature",
                "geometry": new_geojson,
                "properties": properties,
            }
            features.append(feature)

        return Response({
            "type": "FeatureCollection",
            "features": features
        })


class ConflictViewSet(BaseStatusViewSet):
    queryset = Conflict.objects.all()\
        .prefetch_related("projects")
    serializer_class = ConflictFullSerializer

    def get_serializer_class(self):
        action_serializer = {
            'list': ConflictSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
