from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from api.merge_mix import MergeSerializerMixin
from api.pagination import CustomPagination
from rest_framework.filters import SearchFilter, OrderingFilter

from api.views.confirm_delete import CustomDeleteMixin


class UnaccentSearchFilter(SearchFilter):

    def construct_search(self, field_name, queryset):
        from django.db.models.constants import LOOKUP_SEP
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
            return LOOKUP_SEP.join([field_name, lookup])
        else:
            return LOOKUP_SEP.join([field_name, 'unaccent', 'icontains'])


class BaseViewSet(CustomDeleteMixin, viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    # filterset_class = FilterSet
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['name']


class OrderingAutoFilter(OrderingFilter):

    def get_valid_fields(self, queryset, view, context={}):
        from work_flux.models import StatusControl
        valid_fields = getattr(view, 'ordering_fields', self.ordering_fields)

        if valid_fields is None:
            return super().get_valid_fields(queryset, view, context)

        final_valid_fields = super().get_valid_fields(queryset, view, context)

        if '__auto__' in valid_fields:
            all_fields = queryset.model._meta.fields
            for field in all_fields:
                if field.many_to_one:
                    if issubclass(field.related_model, StatusControl):
                        field_str = f'{field.name}__order'
                        final_valid_fields.append((field_str, field_str))
                elif field.primary_key:
                    final_valid_fields.append((field.name, field.name))
                elif field.name in ['name', 'title', 'order']:
                    final_valid_fields.append((field.name, field.name))
        return final_valid_fields


class BaseStatusViewSet(BaseViewSet):
    filterset_fields = ['status_validation']
    ordering_fields = ['__auto__']
    filter_backends = [
        UnaccentSearchFilter, DjangoFilterBackend, OrderingAutoFilter]


# class UnaccentMixin(viewsets.GenericViewSet):
#
#     search_fields = ['name']
#
#     def filter_queryset(self, queryset):
#         from django.db.models import Q
#         queryset = super().filter_queryset(queryset)
#         search_query = self.request.query_params.get('q', '')
#         print('filter_queryset, search_query: ', search_query)
#         print('search_fields: ', self.search_fields)
#         if search_query:
#             filter_query = Q()
#             for field in self.search_fields:
#                 filter_query |= Q(**{f'{field}__unaccent__icontains': search_query})
#                 # filter_query |= Q(**{f'{field}__icontains': search_query})
#                 print('filter_query: ', filter_query)
#             queryset = queryset.filter(filter_query)
#
#         return queryset
