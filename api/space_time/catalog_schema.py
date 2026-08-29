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
    create_only_nested = True
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
            component="LocationType", hidden=False,
        ),
        ComponentFilter(
            title="Marcada en el mapa", field="has_geo_data",
            component="TripleBooleanFilter", hidden=True,
        ),
        ComponentFilter(
            title="Pendientes de ubicación", field="pending",
            component="OnlyByFilter", hidden=True,
            description="Te muestra las ubicaciones de proyectos a las "
                        "que todavía les falta algo para quedar listas. "
                        "Para ver en qué estatus va cada una, usa el "
                        "filtro de estatus de ubicación.",
            custom_options=[
                {"plural_name": "Sin marca en el mapa",
                 "value": "no_geometry",
                 "description": "Todavía no están marcadas en el mapa, ni "
                                "con un punto ni con un trazo."},
                {"plural_name": "Sin municipio", "value": "no_municipality",
                 "description": "Ya están marcadas en el mapa, pero nadie "
                                "anotó a qué municipio pertenecen."},
                {"plural_name": "Completas sin aprobar",
                 "value": "complete_unapproved",
                 "description": "Ya tienen su estado y su municipio y "
                                "están marcadas en el mapa, solo les falta "
                                "que alguien las apruebe."},
                {"plural_name": "Alguno de los casos anteriores",
                 "value": "any_pending",
                 "description": "Junta en una sola lista las ubicaciones "
                                "con cualquiera de los pendientes de "
                                "arriba."},
                {"plural_name": "Sin localidad", "value": "no_locality",
                 "description": "Ya están marcadas en el mapa, pero nadie "
                                "anotó en qué localidad quedan. No entra "
                                "en «alguno de los casos anteriores»: hay "
                                "ubicaciones que no corresponden a "
                                "ninguna localidad."},
            ],
        ),
    ]