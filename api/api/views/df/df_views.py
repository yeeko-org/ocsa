from api.views.common_views import (
    OnlyByFilterMixin, BaseStatusViewSet, BaseGenericViewSet)
from api.views.df.serializers import (
    DisplacementSerializer, DisplacementListSerializer,
    DimensionSerializer, PopulationSizeSerializer,
    TemporalitySerializer)

from df.models import (
    Displacement, Dimension, PopulationSize, Temporality)


class DisplacementFilter(OnlyByFilterMixin):
    only_options = ["event", "impact"]

    class Meta:
        model = Displacement
        fields = ['only_by', 'dimension', 'population_size']


class DisplacementViewSet(BaseStatusViewSet):
    queryset = Displacement.objects.all()
    serializer_class = DisplacementSerializer
    filterset_class = DisplacementFilter

    def get_serializer_class(self):
        action_serializer = {
            'list': DisplacementListSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class DimensionViewSet(BaseGenericViewSet):
    queryset = Dimension.objects.all()
    serializer_class = DimensionSerializer


class PopulationSizeViewSet(BaseStatusViewSet):
    queryset = PopulationSize.objects.all()
    serializer_class = PopulationSizeSerializer


class TemporalityViewSet(BaseGenericViewSet):
    queryset = Temporality.objects.all()
    serializer_class = TemporalitySerializer
