from rest_framework.response import Response

from api.views.space_time import ListSetMixin, StateReportSerializer, StateRetrieveSerializer
from space_time.models import State, Location


class StateReportViewSet(ListSetMixin):
    queryset = State.objects.all()
    serializer_class = StateReportSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StateRetrieveSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        from django.db.models import Count, Q
        queryset = self.filter_queryset(self.get_queryset())
        # Annotate with counts by status_validation
        # queryset = queryset.annotate(
        #     locations__total=Count('locations'
        # ).order_by('state__name')
        stats = Location.objects.filter(
            project__isnull=False, state__isnull=False
        ).values(
            'state',
            'project__status_validation'
        ).annotate(
            count=Count('project', distinct=True)
        ).order_by('project__status_validation')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
