from django.db.models import Count
from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from actor.models import Actor

from api.pagination import CustomPagination
from api.views.actor.massive_chages_serializers import MassiveChangeSerializer
from api.views.actor.serializers import (
    ActorBasicSerializer, ActorCreateSerializer, ActorEditeSerializer,
    ActorFullSerializer)


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

    class Meta:
        model = Actor
        fields = {
            'sector': ['exact'],
            'indigenous_group': ['exact'],
            'belongs': ['exact'],
        }


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()\
        .annotate(projects_count=Count('participants'))\
        .select_related("parent_actor")\
        .prefetch_related("participants", "origin_references")
    permission_classes = [permissions.IsAuthenticated]

    pagination_class = CustomPagination

    filterset_class = ActorFilter

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "title",
    ]
    ordering_fields = ['id', 'name', 'projects_count']
    ordering = ['id']

    serializer_class = ActorBasicSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ActorFullSerializer,
            'create': ActorCreateSerializer,
            'update': ActorEditeSerializer,
            'massive_changes': MassiveChangeSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)

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
