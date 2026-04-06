from ps_schema.registry import (
    catalog_registry, CatalogSchema,
    collection_registry, CollectionSchema, FilterRef,
    FilterGroupSchema,
)
from impact.models import ImpactGroup, ImpactType, ImpactSubtype, Impact
from api.views.catalogs.serializers import ImpactTypeFullSerializer


@catalog_registry.register
class ImpactGroupSchema(CatalogSchema):
    model = ImpactGroup
    level = "category_group"
    name = "Grupo de Afectación"
    plural_name = "Grupos de Afectación"
    permission = "admin"


@catalog_registry.register
class ImpactTypeSchema(CatalogSchema):
    model = ImpactType
    level = "category_type"
    plural_name = "Tipos de Afectación"
    can_merge = True
    count_fields = {
        "impact_subtype_count": "impact_subtypes",
        "mentions_count": "impact",
    }
    filterset_fields = ["impact_group", "status_validation"]
    full_serializer_class = ImpactTypeFullSerializer


@catalog_registry.register
class ImpactSubtypeSchema(CatalogSchema):
    model = ImpactSubtype
    level = "category_subtype"
    plural_name = "Subtipos de Afectación"
    optional_category = True
    open_insertion = False
    can_merge = True
    count_fields = {"impacts_count": "impact"}
    filterset_fields = ["impact_type", "status_validation"]


@catalog_registry.register_filter_group
class ImpactTypesFilterGroup(FilterGroupSchema):
    key_name = "impact_types"
    name = "Clasificación de Afectación"
    plural_name = "Clasificaciones de Afectación"
    main_collection = "impact-impact"
    category_group = ImpactGroup
    category_type = ImpactType
    category_subtype = ImpactSubtype
    addl_config = {"short_prev": "Af.", "prev": "Afectación"}


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

from api.views.impact import ImpactViewSet
from api.export_blocks.impact import ImpactExport


@collection_registry.register
class ImpactSchema(CollectionSchema):
    model = Impact
    level = "secondary"
    viewset_class = ImpactViewSet
    color = "indigo"
    can_massive_edit = True
    xls_export_class = ImpactExport
    all_filters = [
        FilterRef("impact_types"),
    ]
