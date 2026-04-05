from typing import TYPE_CHECKING

from rest_framework.decorators import action
from django.http import FileResponse
from yeeko_xlsx_export.generic import export_xlsx
from api.export_blocks.base import ExportBlock
from api.export_blocks.actor import ActorExportBlock
from api.export_blocks.mention import MentionExportBlock
from api.export_blocks.event import EventExportBlock
from api.export_blocks.location import LocationExportBlock
from api.export_blocks.participant import ParticipantExportBlock


if TYPE_CHECKING:
    from rest_framework.viewsets import ModelViewSet
else:
    class ModelViewSet:
        pass


class ExportXlsMixin(ModelViewSet):
    """Adds a GET /export_xls/ action to any ViewSet.

    Data flow:
        get_query_for_export_xls() → get_export_rows() → export_xls()

    xls_attrs: ordered list of column descriptors for this ViewSet's sheet.
        Plain field dicts and special_group entries can be mixed freely.
    extra_attrs: named registry of ExportBlock classes available as
        special_group values in xls_attrs. Override per ViewSet to add or
        replace entries.

    Always override get_export_rows() to use ExportBlock.extract() directly
    — the default falls back to the serializer, which is slower and builds
    fields not always intended for export.
    Always override get_query_for_export_xls() to optimize the queryset for
    the exact relations the export touches.
    """

    xls_attrs: list = []
    final_xls_attrs: list = []
    additional_groups: list[str] = []
    extra_attrs: dict = {
        "location": LocationExportBlock,
        "mention": MentionExportBlock,
        "actor": ActorExportBlock,
        "event": EventExportBlock,
        "participant": ParticipantExportBlock,
    }

    max_decimal: int = 2

    def get_query_for_export_xls(self):
        return self.filter_queryset(self.get_queryset())

    def get_export_rows(self, queryset) -> list:
        # Default path — override with ExportBlock.extract() for performance.
        serializer = self.get_serializer(queryset, many=True)
        return list(serializer.data)

    def get_annotations(self, target):
        from space_time.models import Location
        from django.db.models import OuterRef, Subquery

        query_loc = {target: OuterRef('id')}
        max_priority_location = Location.objects.filter(**query_loc)\
            .order_by('-status_location__priority')

        annotations = {
            "location_id": Subquery(max_priority_location.values('id')[:1])
        }
        for field in LocationExportBlock.annotation_fields:
            annotations[field] = Subquery(
                max_priority_location.values(field)[:1]
            )
        return annotations

    @action(detail=False, methods=['get'])
    def export_xls(self, request):
        data = self.get_export_rows(self.get_query_for_export_xls())
        is_logged_in = request.user and request.user.is_authenticated
        # print("is_logged_in", is_logged_in)

        name = getattr(self, 'xls_name', 'Exportación sin nombre')
        if not name:
            name = self.queryset.model._meta.verbose_name_plural
        xls_attrs = getattr(self, 'xls_attrs', [])
        for group in self.additional_groups:
            if group in self.extra_attrs:
                xls_attrs += self.extra_attrs[group]['attrs']
        # final_xls_attrs = xls_attrs.copy()
        self.final_xls_attrs = []
        for xls_attr in xls_attrs:
            add_to_final = True
            if conditions := xls_attr.get('conditions'):
                for condition in conditions:
                    if condition == 'only_logged_in' and not is_logged_in:
                        add_to_final = False
            if add_to_final:
                self.add_final_xls_attr(xls_attr)

        # print("final_xls_attrs", self.final_xls_attrs)
        columns_width = [
            row.get('width', 20) for row in self.final_xls_attrs]
        headers = [
            row.get('name', '') for row in self.final_xls_attrs]
        # columns_width_pixel
        max_decimal = getattr(self, 'max_decimal', 5)

        table_data = [headers]
        for row in data:
            row_data = []
            # table_data.append([row.get(attr['field'], '') for attr in attrs])
            for attr in self.final_xls_attrs:
                field = attr.get('field', '')
                if field:
                    value = row
                    if attr.get('subquery'):
                        # Flat ORM annotation — read directly from top-level row.
                        value = row.get(field, '')
                    else:
                        # "a__b__c" → row["a"]["b"]["c"] via chained .get().
                        for key in field.split('__'):
                            try:
                                value = value.get(key, '')
                            except AttributeError:
                                value = ''
                    if operation := attr.get('operation'):
                        try:
                            if operation == 'min':
                                value = min(value)
                            elif operation == 'max':
                                value = max(value)
                            if operation == 'count':
                                value = len(value)
                        except Exception:
                            pass
                    row_data.append(value)
                else:
                    row_data.append('')
            table_data.append(row_data)

        # print(table_data)

        response = export_xlsx(
            in_memory=True, data=[{
                "name": name,
                "table_data": table_data,
                "columns_width": columns_width,
                # "columns_width_pixel": columns_width,
                "max_decimal": max_decimal
            }])

        response.seek(0)
        return FileResponse(response, as_attachment=True, filename=f"{name}.xlsx")

    def add_final_xls_attr(self, xls_attr: dict) -> None:
        # Dispatches between ExportBlock subclasses (current) and legacy
        # {"attrs": [...]} dicts. Both paths respect the optional `preset`,
        # which prefixes all column fields at expansion time (never mutates
        # the original block).
        if special_group := xls_attr.get('special_group'):
            entry = self.extra_attrs.get(special_group)
            if entry is None:
                return
            preset = xls_attr.get('preset')
            if isinstance(entry, type) and issubclass(entry, ExportBlock):
                attrs = (
                    entry.prefixed(preset) if preset else list(entry.columns)
                )
            else:
                # Legacy: {"attrs": [...]} — build copies para no mutar
                group_attrs = entry.get('attrs', [])
                if preset:
                    attrs = [
                        {**attr, "field": f"{preset}__{attr['field']}"}
                        for attr in group_attrs
                    ]
                else:
                    attrs = group_attrs
            self.final_xls_attrs.extend(attrs)
        else:
            self.final_xls_attrs.append(xls_attr)
