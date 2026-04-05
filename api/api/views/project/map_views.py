from django_filters import FilterSet, NumberFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from space_time.models import Location
from . import LocationVizSerializer
from .map_serializers import (
    ProjectMapSerializer, MentionMapSerializer, ImpactMapSerializer,
    EventMapSerializer)
from api.views.common_views import UnaccentSearchFilter
from project.models import Project
from ...permissions import LocationPermission


class ProjectMapViewSet(GenericViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.AllowAny]

    # queryset = Project.objects.all().prefetch_related("locations").distinct()
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

    serializer_class = ProjectMapSerializer
    filter_backends = [
        UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['name',
                     'alternative_name',
                     '=proyecto_id_ref']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(
                status_validation__is_public=True)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        from source.models import Mention
        from impact.models import Impact
        from event.models import Event
        project = self.get_object()

        project_serializer = self.get_serializer(project)
        data = project_serializer.data

        relates = ['conflict']
        # prefetches = ['conflict']
        direct_mentions = Mention.objects \
            .filter(project=project) \
            .select_related('note')

        if project.is_grouper:
            children_mentions = Mention.objects\
                .filter(project__parent_project=project)\
                .select_related('note')
            mention_qs = direct_mentions | children_mentions

        elif project.parent_project:
            parent_mentions = Mention.objects\
                .filter(project=project.parent_project)\
                .select_related('note')
            brother_mentions = Mention.objects\
                .filter(project__parent_project=project.parent_project)\
                .select_related('note')
            mention_qs = brother_mentions | parent_mentions

        else:
            mention_qs = direct_mentions

        mention_qs = mention_qs.order_by('-note__date')
        mentions_serializer = MentionMapSerializer(mention_qs, many=True)
        data['mentions'] = mentions_serializer.data

        mention_ids = mention_qs.values_list('id', flat=True)

        impacts_qs = Impact.objects.filter(mention__in=mention_ids)
        # .select_related('impact_type', 'impact_subtype', 'mention')
        impacts_serializer = ImpactMapSerializer(impacts_qs, many=True)
        data['impacts'] = impacts_serializer.data

        events_qs = Event.objects.filter(mention__in=mention_ids)
        events_serializer = EventMapSerializer(events_qs, many=True)
        data['events'] = events_serializer.data

        return Response(data)


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
        # extra_large_locations = []
        for loc_data in serializer_other.data:
            # if loc_data["id"] == 2513 or loc_data["id"] == 12306:
            #     print(f"\n\nDebugging location id {loc_data['id']}:")
            #     print(loc_data)
            geojson = loc_data.get('geojson', None)
            new_geometry = None
            if my_features := geojson.get('features'):
                new_geometry = my_features[0].get('geometry').copy()

            if not new_geometry and geojson is not None:
                geometry = geojson.get('geometry', None)
                new_geometry = geometry.copy()

            if new_geometry:
                coordinates = new_geometry.get('coordinates', [])
                # if len(coordinates) > 100:
                #     extra_large_locations.append(loc_data)
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
                new_geometry['coordinates'] = new_coordinates

            else:
                continue

            properties = {}
            for key in keep_fields:
                properties[key] = loc_data.get(key)

            feature = {
                "type": "Feature",
                "geometry": new_geometry,
                "properties": properties,
            }
            features.append(feature)

        return Response({
            "type": "FeatureCollection",
            "features": features
        })
