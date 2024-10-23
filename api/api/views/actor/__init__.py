from django.db.models import F
from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.request import Request

from actor.models import Actor, Member, OriginReference, Participant

from api.merge_mix import FromToModelSerializer, MergeSerializerMixin
from api.pagination import CustomPagination
from api.views.actor.massive_chages_serializers import MassiveChangeSerializer
from api.views.actor.serializers import (
    ActorBaseSerializer, ActorMiniSerializer, ActorCreateSerializer, ActorEditeSerializer,
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
            'network_seq': ['exact'],
        }


class ActorViewMixin(MergeSerializerMixin, viewsets.GenericViewSet):
    request: Request
    queryset = Actor.objects.all().distinct()\
        .annotate(
            sector_group=F('sector__sector_group')
        )\
        .select_related(
        "parent_actor", "parent_actor__sector", "status_validation")\
        .prefetch_related("participants", "origin_references")\

    permission_classes = [permissions.AllowAny]

    pagination_class = CustomPagination

    filterset_class = ActorFilter

    filter_backends = [OrderingFilter, DjangoFilterBackend]

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

    def get_from_obj(self, from_id):
        return Actor.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Member.objects.filter(actor_individual=from_obj)\
            .update(actor_individual=to_obj)
        Member.objects.filter(actor_collective=from_obj)\
            .update(actor_collective=to_obj)
        Participant.objects.filter(actor=from_obj)\
            .update(actor=to_obj)
        OriginReference.objects.filter(actor=from_obj)\
            .update(actor=to_obj)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        search_query = self.request.query_params.get('q', '')
        if search_query:
            queryset = queryset.filter(name__unaccent__icontains=search_query)
            # queryset = queryset.filter(name__icontains=search_query)

        return queryset


class ActorViewSet(ActorViewMixin, viewsets.ModelViewSet):

    serializer_class = ActorBaseSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ActorFullSerializer,
            'create': ActorCreateSerializer,
            'update': ActorEditeSerializer,
            'massive_changes': MassiveChangeSerializer,
            'merge': FromToModelSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)


class ActorMiniListViewSet(ActorViewMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ActorMiniSerializer
