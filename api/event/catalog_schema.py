from ps_schema.registry import (
    catalog_registry, CatalogSchema,
    collection_registry, CollectionSchema, FilterRef,
    FilterGroupSchema
)
from api.views.common_views import MassiveEdit
from event.models import (
    InvolvedRole, EventGroup, EventType, Purpose, Event, Involved)


@catalog_registry.register
class InvolvedRoleSchema(CatalogSchema):
    model = InvolvedRole
    level = "category_subtype"
    open_insertion = False
    cat_params = {"select_component": "autocomplete"}
    filter_group_key = "involved_roles"
    filter_group_addl_config = {"subtype_is_autocomplete": True}


@catalog_registry.register
class EventGroupSchema(CatalogSchema):
    model = EventGroup
    level = "category_type"
    name = "Grupo de Evento"
    plural_name = "Grupos de Eventos"
    open_insertion = False
    base = "viewset"
    permission = "admin"
    count_fields = {"event_types_count": "event_types"}


@catalog_registry.register
class EventTypeSchema(CatalogSchema):
    model = EventType
    level = "category_subtype"
    name = "Tipo de Evento"
    plural_name = "Tipos de Eventos"
    open_insertion = True
    can_merge = True
    can_massive_edit = True
    extra_mixins = [MassiveEdit]
    count_fields = {"events_count": "events"}
    filterset_fields = ['status_validation', 'event_group']


@catalog_registry.register
class PurposeSchema(CatalogSchema):
    model = Purpose
    level = "category_subtype"
    name = "Propósito del Mecanismo"
    plural_name = "Propósitos de Mecanismos"
    permission = "admin"
    count_fields = {"events_count": "events"}
    filterset_fields = []
    filter_group_key = "purposes"


@catalog_registry.register_filter_group
class EventTypesFilterGroup(FilterGroupSchema):
    key_name = "event_types"
    name = "Clasificación de Evento"
    plural_name = "Clasificaciones de Eventos"
    main_collection = "event-event"
    category_type = EventGroup
    category_subtype = EventType
    addl_config = {
        "short_prev": "Ev.",
        "prev": "Evento",
        "subtype_is_autocomplete": True,
        "special_group": "event_group",
    }


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

from api.views.event import EventViewSet, InvolvedViewSet
from api.export_blocks.event import EventExport


@collection_registry.register
class EventSchema(CollectionSchema):
    model = Event
    level = "secondary"
    viewset_class = EventViewSet
    icon = "notifications_active"
    color = "lime"
    can_massive_edit = True
    xls_export_class = EventExport
    all_filters = [
        FilterRef("event_types"),
        FilterRef("purposes", hidden=True),
        FilterRef("sectors", hidden=True),
        FilterRef("involved_roles", hidden=True),
        FilterRef("participant_types", hidden=True),
    ]


@collection_registry.register
class InvolvedSchema(CollectionSchema):
    model = Involved
    level = "relational"
    viewset_class = InvolvedViewSet

