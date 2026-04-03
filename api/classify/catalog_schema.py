from ps_schema.registry import catalog_registry, CatalogSchema, FilterGroupSchema
from classify.models import (
    IndigenousGroup, Sector, SectorGroup,
    ParticipantGroup, ParticipantType, Belong, Country,
    InterestGroup, InterestType, InterestSubtype,
)
from api.views.actor.classify_serializers import (
    IndigenousGroupFullSerializer,
    ParticipantGroupFullSerializer,
)


@catalog_registry.register
class IndigenousGroupSchema(CatalogSchema):
    model = IndigenousGroup
    level = "category_subtype"
    open_insertion = True
    can_merge = True
    cat_params = {"select_component": "autocomplete"}
    count_fields = {"count": "actors"}
    full_serializer_class = IndigenousGroupFullSerializer
    filter_group_key = "indigenous_groups"
    filter_group_addl_config = {"subtype_is_autocomplete": True}


@catalog_registry.register
class SectorGroupSchema(CatalogSchema):
    model = SectorGroup
    level = "category_type"
    open_insertion = True
    can_merge = True
    count_fields = {"sectors_count": "sectors"}


@catalog_registry.register
class SectorSchema(CatalogSchema):
    model = Sector
    level = "category_subtype"
    open_insertion = True
    can_merge = True
    count_fields = {"actors_count": "actors"}
    filterset_fields = ["status_validation", "sector_group"]


@catalog_registry.register
class ParticipantGroupSchema(CatalogSchema):
    model = ParticipantGroup
    level = "category_type"
    name = "Tipo de Part."
    plural_name = "Tipos de Participación"
    count_fields = {"participant_types_count": "participant_types"}
    filterset_fields = []
    full_serializer_class = ParticipantGroupFullSerializer


@catalog_registry.register
class ParticipantTypeSchema(CatalogSchema):
    model = ParticipantType
    level = "category_subtype"
    name = "Subtipo de Part."
    plural_name = "Subtipos de Participación en Proyecto"
    open_insertion = True
    can_merge = True
    count_fields = {"actors_count": "participants__actor"}
    filterset_fields = ["status_validation", "participant_group"]


@catalog_registry.register
class BelongSchema(CatalogSchema):
    model = Belong
    level = "category_subtype"
    open_insertion = False
    can_merge = True
    count_fields = {"actors_count": "actors"}
    filterset_fields = []
    filter_group_key = "belongs"


@catalog_registry.register
class CountrySchema(CatalogSchema):
    model = Country
    level = "category_subtype"
    name = "País"
    open_insertion = True
    cat_params = {"select_component": "autocomplete"}
    count_fields = {"actors_count": "actors"}
    filterset_fields = []
    filter_group_key = "countries"
    filter_group_addl_config = {"subtype_is_autocomplete": True}


@catalog_registry.register
class InterestGroupSchema(CatalogSchema):
    model = InterestGroup
    level = "category_type"
    base = "viewset"
    permission = "admin"


@catalog_registry.register
class InterestTypeSchema(CatalogSchema):
    model = InterestType
    level = "category_subtype"
    open_insertion = True
    can_merge = True


@catalog_registry.register
class InterestSubtypeSchema(CatalogSchema):
    model = InterestSubtype
    level = "category_subtype"
    open_insertion = True
    can_merge = True


@catalog_registry.register_filter_group
class ParticipantTypesFilterGroup(FilterGroupSchema):
    key_name = "participant_types"
    name = "Tipo de Participación"
    plural_name = "Tipos de Participación"
    main_collection = "actor-actor"
    category_type = ParticipantGroup
    category_subtype = ParticipantType
    addl_config = {"special_group": "participant_group"}


@catalog_registry.register_filter_group
class SectorsFilterGroup(FilterGroupSchema):
    key_name = "sectors"
    name = "Sector"
    plural_name = "Sectores"
    main_collection = "actor-actor"
    category_type = SectorGroup
    category_subtype = Sector
    addl_config = {"subtype_is_autocomplete": True, "open_search": True}


@catalog_registry.register_filter_group
class InterestTypesFilterGroup(FilterGroupSchema):
    key_name = "interest_types"
    name = "Tipo de interés"
    plural_name = "Tipos de interés"
    main_collection = "actor-interest"
    category_group = InterestGroup
    category_type = InterestType
    category_subtype = InterestSubtype
    addl_config = {"short_prev": "Int.", "prev": "Interés"}
