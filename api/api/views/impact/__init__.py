from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.pagination import CustomPagination
from api.views.common_views import (
    ClickHistoryMixin, MassiveEdit, UnaccentSearchFilter,
)
from api.views.note.serializers import ImpactFullSerializer
from api.views.project.list_serializers import (
    ImpactSimpleSerializer,
)
from impact.models import Impact


class ImpactViewSet(
    ClickHistoryMixin, MassiveEdit, viewsets.ModelViewSet
):
    pagination_class = CustomPagination
    queryset = Impact.objects.all()
    is_mention_child = True

    serializer_class = ImpactSimpleSerializer
    filter_backends = [UnaccentSearchFilter, DjangoFilterBackend]
    search_fields = ['description']
    filterset_fields = ['impact_type', 'impact_subtype']

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': ImpactFullSerializer,
            'update': ImpactFullSerializer,
            'create': ImpactFullSerializer,
        }
        return action_serializer.get(
            self.action, self.serializer_class
        )