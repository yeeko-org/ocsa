from typing import TYPE_CHECKING

from rest_framework.decorators import action
from django.http import FileResponse
from yeeko_xlsx_export.generic import export_xlsx
from api.views.actor.actor_export import xlsx_actor_group
from api.views.note.mention_export import xlsx_mention_group


if TYPE_CHECKING:
    from rest_framework.viewsets import ModelViewSet
else:
    class ModelViewSet:
        pass


class ExportXlsMixin(ModelViewSet):
    # xls_name: str = "Export"
    xls_attrs: list = []
    final_xls_attrs: list = []
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
            "attrs": xlsx_mention_group,
        },
        "actor": {
            "attrs": xlsx_actor_group
        },
        "event": {
            "attrs": [
                {
                    "name": "ID del evento",
                    "width": 5,
                    "field": "id"
                },
                {
                    "name": "Grupo de evento",
                    "width": 15,
                    "field": "event_type__event_group"
                },
                {
                    "name": "Tipo de evento",
                    "width": 30,
                    "field": "event_type__name"
                },
                {
                    "name": "Descripción del evento",
                    "width": 50,
                    "field": "description"
                },
                {
                    "name": "Mujeres víctimas",
                    "width": 4,
                    "field": "number_women"
                },
                {
                    "name": "Hombres víctimas",
                    "width": 4,
                    "field": "number_men"
                },
                {
                    "name": "Personas víctimas",
                    "width": 4,
                    "field": "number_mix"
                },
                {
                    "name": "Intención del mecanismo",
                    "width": 18,
                    "field": "purpose"
                },
            ]
        },
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
        import json
        serializer = self.get_serializer(
            self.get_query_for_export_xls(), many=True)

        data = serializer.data
        first_item = data[0] if data else None
        serializer_name = serializer.__class__.__name__ if serializer else None
        print("serializer_name", serializer_name)
        if first_item:
            print("first_item", json.dumps(first_item, indent=2))
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

    def add_final_xls_attr(self, xls_attr):
        if special_group := xls_attr.get('special_group'):
            group_attrs = self.extra_attrs \
                .get(special_group, { }) \
                .get('attrs', [])
            if preset := xls_attr.get('preset'):
                final_group_attrs = []
                for group_attr in group_attrs:
                    group_attr['field'] = f"{preset}__{group_attr['field']}"
                    final_group_attrs.append(group_attr)
                self.final_xls_attrs.extend(final_group_attrs)
            else:
                self.final_xls_attrs.extend(group_attrs)
        else:
            self.final_xls_attrs.append(xls_attr)