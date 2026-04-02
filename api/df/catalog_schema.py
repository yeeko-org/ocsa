from ps_schema.registry import (
    catalog_registry, CatalogSchema,
    collection_registry, CollectionSchema, FilterRef, ComponentFilter,
)
from df.models import Dimension, PopulationSize, Temporality, Displacement


@catalog_registry.register
class DimensionSchema(CatalogSchema):
    model = Dimension
    level = "category_subtype"
    base = "generic"
    count_fields = {"displacement_count": "displacements"}
    filter_group_key = "dimensions"
    filter_group_main = "df-displacement"


@catalog_registry.register
class PopulationSizeSchema(CatalogSchema):
    model = PopulationSize
    level = "category_subtype"
    base = "status"
    count_fields = {"displacement_count": "displacements"}
    filter_group_key = "population_sizes"
    filter_group_main = "df-displacement"


@catalog_registry.register
class TemporalitySchema(CatalogSchema):
    model = Temporality
    level = "category_subtype"
    base = "generic"
    count_fields = {"displacement_count": "displacements"}
    filter_group_key = "temporalities"
    filter_group_main = "df-displacement"


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

from api.views.df.df_views import DisplacementViewSet  # noqa: E402


@collection_registry.register
class DisplacementSchema(CollectionSchema):
    model = Displacement
    level = "primary"
    viewset_class = DisplacementViewSet
    name = "Desplazamiento Forzado"
    plural_name = "Desplazamientos Forzados"
    icon = "hiking"
    color = "orange"
    all_filters = [
        FilterRef("dimensions"),
        FilterRef("population_sizes"),
        FilterRef("temporalities"),
        ComponentFilter(
            title="Colección", field="only_by",
            component="OnlyByFilter",
            options=["event", "impact"]),
    ]