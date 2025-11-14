from typing import TYPE_CHECKING

from rest_framework.decorators import action
from django.http import FileResponse
from yeeko_xlsx_export.generic import export_xlsx


if TYPE_CHECKING:
    from rest_framework.viewsets import ModelViewSet
else:
    class ModelViewSet:
        pass


class ExportXlsMixin(ModelViewSet):
    action_add_file_param: str = ""
    # xls_name: str = "Export"
    xls_attrs: list = []
    # add_locations = False
    additional_groups: list[str] = []
    extra_attrs: dict = {
        "location": {
            "attrs": [
                {
                    "name": "ID de ubicación principal",
                    "width": 5,
                    "field": "location_id",
                },
                {
                    "name": "ID de Entidad",
                    "width": 4,
                    "field": "state__inegi_code",
                    "subquery": "locations"
                },
                {
                    "name": "Entidad",
                    "width": 25,
                    "field": "state__short_name",
                    "subquery": "locations"
                },
                {
                    "name": "ID de Municipio",
                    "width": 4,
                    "field": "municipality__inegi_code",
                    "subquery": "locations"
                },
                {
                    "name": "Municipio",
                    "width": 25,
                    "field": "municipality__name",
                    "subquery": "locations"
                },
                {
                    "name": "ID de Localidad",
                    "width": 4,
                    "field": "locality__inegi_code",
                    "subquery": "locations"
                },
                {
                    "name": "Localidad",
                    "width": 25,
                    "field": "locality__name",
                    "subquery": "locations"
                },
                {
                    "name": "Latitud",
                    "width": 12,
                    "field": "latitude",
                    "subquery": "locations"
                },
                {
                    "name": "Longitud",
                    "width": 12,
                    "field": "longitude",
                    "subquery": "locations"
                }
            ],
        },
        "mention": {
            "attrs": [
                {
                    "name": "ID de nota",
                    "width": 5,
                    "field": "mention__note_full__id"
                },
                {
                    "name": "Fecha de nota",
                    "width": 10,
                    "field": "mention__note_full__date"
                },
                {
                    "name": "Título de nota",
                    "width": 40,
                    "field": "mention__note_full__title"
                },
                {
                    "name": "Medio de la nota",
                    "width": 15,
                    "field": "mention__note_full__source"
                },
                {
                    "name": "ID de proyecto",
                    "width": 5,
                    "field": "mention__project_full__id"
                },
                {
                    "name": "Nombre de proyecto",
                    "width": 40,
                    "field": "mention__project_full__name"
                },
                {
                    "name": "ID de conflicto",
                    "width": 5,
                    "field": "conflict__id"
                },
                {
                    "name": "Nombre de conflicto",
                    "width": 30,
                    "field": "conflict__name"
                },
            ],
        }
    }
    # location_attrs = extra_attrs['location']['attrs']

    max_decimal: int = 2

    def get_query_for_export_xls(self):
        return self.filter_queryset(self.get_queryset())

    def get_annotations(self, target):
        from space_time.models import Location
        from django.db.models import OuterRef, Subquery

        query_loc = {target: OuterRef('id')}
        max_priority_location = Location.objects.filter(**query_loc)\
            .order_by('-status_location__priority')

        annotations = {
            "location_id": Subquery(max_priority_location.values('id')[:1])
        }
        location_fields = [
            attr['field'] for attr in self.extra_attrs['location']['attrs']
            if attr.get('subquery') == 'locations'
        ]
        for field in location_fields:
            annotations[field] = Subquery(
                max_priority_location.values(field)[:1]
            )
        return annotations

    @action(detail=False, methods=['get'])
    def export_xls(self, request):
        serializer = self.get_serializer(
            self.get_query_for_export_xls(), many=True)

        data = serializer.data
        is_logged_in = request.user and request.user.is_authenticated
        print("is_logged_in", is_logged_in)

        name = getattr(self, 'xls_name', None)
        if not name:
            name = self.queryset.model._meta.verbose_name_plural
        xls_attrs = getattr(self, 'xls_attrs', [])
        for group in self.additional_groups:
            if group in self.extra_attrs:
                xls_attrs += self.extra_attrs[group]['attrs']
        final_xls_attrs = xls_attrs.copy()
        for xls_attr in xls_attrs:
            conditions = xls_attr.get('conditions', [])
            add_to_final = True
            for condition in conditions:
                if condition == 'only_logged_in' and not is_logged_in:
                    add_to_final = False
            if not add_to_final:
                final_xls_attrs.remove(xls_attr)

        columns_width = [row.get('width', 20) for row in final_xls_attrs]
        headers = [row.get('name', '') for row in final_xls_attrs]
        # columns_width_pixel
        max_decimal = getattr(self, 'max_decimal', 2)

        table_data = [headers]
        for row in data:
            row_data = []
            # table_data.append([row.get(attr['field'], '') for attr in attrs])
            for attr in final_xls_attrs:
                field = attr.get('field', '')
                if field:
                    value = row
                    if attr.get('subquery'):
                        value = row.get(field, '')
                    else:
                        for key in field.split('__'):
                            try:
                                value = value.get(key, '')
                            except AttributeError as e:
                                # print(f"Error accessing {key} in {value}\n{row}")
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
