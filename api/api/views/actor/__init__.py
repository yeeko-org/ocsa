from django.db.models import F
from django_filters import FilterSet, NumberFilter, CharFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from api.permissions import IsFullEditorOrReadOnly, DynamicCatalogPermission
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.request import Request

from actor.models import Actor, Member, OriginReference, Participant

from api.merge_mix import FromToModelSerializer, MergeSerializerMixin
from api.pagination import CustomPagination
from api.views.actor.massive_chages_serializers import MassiveChangeSerializer
from api.views.actor.serializers import (
    ActorBaseSerializer, ActorMiniSerializer, ActorCreateSerializer,
    ActorEditeSerializer, ActorFullSerializer, ActorMiniBaseSerializer
)
from api.views.common_views import UnaccentSearchFilter


class ActorFilter(FilterSet):

    sector_group = NumberFilter(
        field_name='sector__sector_group', lookup_expr='exact')
    interest_group = NumberFilter(
        field_name='participants__interests__interest_type__group',
        lookup_expr='exact')
    interest_type = NumberFilter(
        field_name='participants__interests__interest_type',
        lookup_expr='exact')
    participant_type = NumberFilter(
        field_name='participants__participant_types', lookup_expr='exact')
    participant_group = NumberFilter(
        field_name='participants__participant_types__participant_group',
        lookup_expr='exact')
    belong = CharFilter(field_name='belongs', lookup_expr='exact')
    country = NumberFilter(field_name='countries', lookup_expr='exact')

    class Meta:
        model = Actor
        fields = {
            'sector': ['exact'],
            'indigenous_group': ['exact'],
            # 'belongs': ['exact'],
            'network_seq': ['exact'],
            'status_validation': ['exact'],
        }


class ActorViewMixin(viewsets.GenericViewSet):

    request: Request
    massive_fields = ["sector_id", "status_validation", "parent_actor_id"]
    queryset = Actor.objects.all().distinct()\
        .annotate(
            sector_group=F('sector__sector_group')
        )\
        .select_related("parent_actor")\
        .prefetch_related(
        "participants", "origin_references", "children_actors")

    permission_classes = [DynamicCatalogPermission]

    pagination_class = CustomPagination
    filterset_class = ActorFilter

    filter_backends = [OrderingFilter, DjangoFilterBackend, UnaccentSearchFilter]

    search_fields = ['name', 'alternative_names']
    ordering_fields = ['id', 'name', 'mentions_count', 'status_validation__order']
    ordering = ['id']

    @action(detail=False, methods=['post'])
    def massive_changes(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        sector_id = data.get('sector_id')
        status_validation = data.get('status_validation')
        parent_actor_id = data.get('parent_actor_id')

        update_data = {}

        if sector_id:
            update_data['sector_id'] = sector_id

        if status_validation:
            update_data['status_validation'] = status_validation

        if parent_actor_id:
            update_data['parent_actor_id'] = parent_actor_id

        actors = Actor.objects.filter(id__in=data['actors_ids'])
        actors.update(**update_data)

        return Response({'message': 'Actors updated successfully'})

    @action(detail=False, methods=['post'])
    def simple_massive_changes(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        actors_ids = data.pop('actors_ids')

        actors = Actor.objects.filter(id__in=actors_ids)
        actors.update(**request.data)

        return Response({'message': 'Actors updated successfully'})

    @action(detail=False, methods=['post'])
    def medium_massive_changes(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        elements_ids = data.get('elems_ids')

        update_data = {}
        for field in self.massive_fields:
            if field in data:
                update_data[field] = data[field]

        queryset = self.get_queryset()
        elements = queryset.filter(id__in=elements_ids)
        elements.update(**update_data)

        list_serializer = self.get_serializer(elements, many=True)
        return Response(list_serializer.data)


class ActorViewSet(ActorViewMixin, viewsets.ModelViewSet):

    serializer_class = ActorBaseSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ActorFullSerializer,
            'create': ActorFullSerializer,
            'update': ActorFullSerializer,
            'massive_changes': MassiveChangeSerializer,
            'merge': FromToModelSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    @action(detail=True, methods=['delete'])
    def delete_other_parents(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        actor = self.get_object()
        actor.others_parents.clear()
        return Response({'message': 'Other parents deleted successfully'})



class ActorMiniListViewSet(ActorViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Actor.objects.all().distinct()\
        .annotate(
            sector_group=F('sector__sector_group')
        )\
        .select_related("parent_actor")\
        .prefetch_related()
    serializer_class = ActorMiniBaseSerializer


