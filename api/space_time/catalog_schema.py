from ps_schema.registry import catalog_registry, collection_registry
from ps_schema.schemas import (
    CatalogSchema, CollectionSchema, FilterRef, ComponentFilter,
)
from space_time.models import State, Location
from api.views.space_time import StateListViewSet, LocationViewSet


@catalog_registry.register
class StateSchema(CatalogSchema):
    model = State
    level = "category_subtype"
    name = "Estado"
    plural_name = "Estados"
    viewset_class = StateListViewSet
    filter_group_key = "states"


@collection_registry.register
class LocationSchema(CollectionSchema):
    model = Location
    level = "primary"
    name = "Ubicación"
    plural_name = "Ubicaciones"
    viewset_class = LocationViewSet
    can_massive_edit = True
    sort_fields = [
        'id',
        'status_location__order',
        {'mentions_count': 'Cantidad de menciones'},
    ]
    all_filters = [
        FilterRef("states", can_massive_edit=True),
        ComponentFilter(
            title="Colección", field="only_by",
            component="OnlyByFilter",
            options=["project", "event", "impact"],
        ),
        ComponentFilter(
            title="Tipo de ubicación", field="type_location",
            component="LocationType", hidden=True,
        ),
        ComponentFilter(
            title="Con geometría", field="has_geo_data",
            component="TripleBooleanFilter", hidden=True,
        ),
        ComponentFilter(
            title="Completitud", field="completeness",
            component="OnlyByFilter", hidden=True,
            custom_options=[
                {"plural_name": "Completas sin promover",
                 "value": "complete_unpromoted"},
                {"plural_name": "Incompletas sin promover",
                 "value": "incomplete_unpromoted"},
                {"plural_name": "Aprobadas incompletas",
                 "value": "approved_incomplete"},
            ],
        ),
    ]