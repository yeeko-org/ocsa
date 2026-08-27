import logging

from django.db.models import Prefetch
from django_filters import FilterSet, NumberFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from space_time.geometry import to_feature
from space_time.models import Location
from api.views.project import LocationVizSerializer
from .serializers import (
    ProjectMapSerializer, MentionMapSerializer, ImpactMapSerializer,
    EventMapSerializer, NoteDeepMapSerializer)
from .visibility import visible_locations, visible_mentions, visible_projects
from api.views.common_views import UnaccentSearchFilter
from project.models import Project
from source.models import Note, Mention
from api.permissions import LocationPermission

logger = logging.getLogger(__name__)


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
            queryset = visible_projects(queryset)
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

        # Un filtro sobre la unión equivale a filtrar cada rama. Sin esto la
        # ficha lista menciones cuya nota `note_map` le niega al visitante, y
        # las de proyectos hermanos o padre que el mapa no muestra: el pin
        # fantasma de `adr-0022` por la puerta de al lado.
        if not request.user.is_authenticated:
            mention_qs = visible_mentions(mention_qs)

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


class NoteMapViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    """Endpoint público de solo lectura para una nota tal como se
    muestra en el mapa. Devuelve metadatos de la nota (sin cuerpo del
    artículo, por restricción de copyright) más las menciones que la
    nota contiene, cada una con su proyecto y sus impactos, eventos e
    historial de estatus anidados.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = NoteDeepMapSerializer

    queryset = Note.objects.all().select_related('source').prefetch_related(
        Prefetch(
            'mentions',
            queryset=Mention.objects.select_related(
                'project',
                'project__megaproject_type',
                'project__parent_project',
            ).prefetch_related(
                'status_history',
                'impacts',
                'events',
            ),
        ),
    )

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.filter(status_register__is_public=True)
        return qs


class ProjectLocationFilter(FilterSet):
    extractivism_type = NumberFilter(
        field_name='project__megaproject_type__extractivism_types',
        lookup_expr='exact')

    class Meta:
        model = Location
        fields = ["state", "type_location"]


class ProjectLocationViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [LocationPermission]

    queryset = Location.objects.all().order_by('project__name')
        # .filter(project__isnull=False)\
        # .select_related("project")
        # .select_related("project", "project__megaproject_type")

    # queryset = Project.objects.all().prefetch_related("locations").distinct()
    serializer_class = LocationVizSerializer
    filter_backends = [UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['state__name',
                     'municipality__name',
                     'locality__name',
                     'project__name']

    def get_queryset(self):
        # El geojson es el mismo para quien está dentro y quien no: el
        # mapa muestra lo público, la edición vive en otros endpoints.
        return visible_locations(super().get_queryset()).select_related(
            "project")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        location_points = queryset.filter(
            type_location='point', latitude__isnull=False,
            longitude__isnull=False)
        other_locations = queryset.\
            filter(geojson__isnull=False)\
            .exclude(type_location='point')

        keep_fields = [
            "id", "state", "municipality", "locality", "project"]
        features = []

        for serializer in (self.get_serializer(location_points, many=True),
                           self.get_serializer(other_locations, many=True)):
            for loc_data in serializer.data:
                properties = {key: loc_data.get(key) for key in keep_fields}
                try:
                    feature = to_feature(loc_data, properties)
                except Exception:
                    # El mapa es público: una fila con geometría inconsistente
                    # se omite, nunca tumba la respuesta completa.
                    logger.warning(
                        "Ubicación %s con geojson inservible, se omite del "
                        "mapa", loc_data.get("id"), exc_info=True)
                    continue
                if feature is not None:
                    features.append(feature)

        return Response({
            "type": "FeatureCollection",
            "features": features
        })
