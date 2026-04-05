from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.pagination import CustomPagination
from api.export_blocks.impact import ImpactExportBlock
from api.export_blocks.location import LocationExportBlock
from api.export_blocks.mention import MentionExportBlock
from api.views.action_export_xls import ExportXlsMixin
from api.views.common_views import ClickHistoryMixin, MassiveEdit, UnaccentSearchFilter
from api.views.note.serializers import ImpactFullSerializer
from api.views.project.list_serializers import ImpactSimpleSerializer
from impact.models import Impact


class ImpactViewSet(
    ClickHistoryMixin, MassiveEdit, ExportXlsMixin, viewsets.ModelViewSet
):
    pagination_class = CustomPagination
    queryset = Impact.objects.all()
    is_mention_child = True

    xls_name = "Exportación de Afectaciones"
    xls_attrs = [
        *ImpactExportBlock.columns,
        {"special_group": "mention"},
        {"special_group": "location"},
    ]

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
        return action_serializer.get(self.action, self.serializer_class)

    def get_query_for_export_xls(self):
        annotations = self.get_annotations(target='impact')
        queryset = self.get_queryset() \
            .annotate(**annotations) \
            .select_related(
                'mention', 'mention__note',
                'mention__note__source',
                'mention__project', 'mention__project__conflict',
                'impact_subtype',
                'impact_type', 'impact_type__impact_group',
            ) \
            .distinct()
        return self.filter_queryset(queryset)

    def get_export_rows(self, queryset) -> list[dict]:
        return [
            {
                **ImpactExportBlock.extract(obj),
                **MentionExportBlock.extract(obj),
                **LocationExportBlock.extract(obj),
            }
            for obj in queryset
        ]
