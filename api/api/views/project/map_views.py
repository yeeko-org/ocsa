from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .map_serializers import (
    ProjectMapSerializer, MentionMapSerializer, ImpactMapSerializer,
    EventMapSerializer)
from api.views.common_views import UnaccentSearchFilter
from project.models import Project

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
