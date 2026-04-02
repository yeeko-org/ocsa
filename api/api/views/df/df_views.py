
from api.views.common_views import (
    OnlyByFilterMixin, BaseStatusViewSet)
from api.views.df.serializers import (
    DisplacementListSerializer, DisplacementFullSerializer)

from df.models import Displacement


class DisplacementFilter(OnlyByFilterMixin):
    only_options = ["event", "impact"]

    class Meta:
        model = Displacement
        fields = ['only_by', 'dimension', 'population_size']


class DisplacementViewSet(BaseStatusViewSet):
    queryset = Displacement.objects.all()
    serializer_class = DisplacementFullSerializer
    filterset_class = DisplacementFilter

    def get_serializer_class(self):
        action_serializer = {
            'list': DisplacementListSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)
