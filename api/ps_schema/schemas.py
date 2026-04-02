"""
Declaraciones de schema para colecciones del sistema.

Dos familias, separadas por level:

  CatalogSchema   — category_group / category_type / category_subtype
  CollectionSchema — primary / secondary / relational

Más FilterGroupSchema para grupos de filtros multi-nivel.

Los registries (catalog_registry, collection_registry) viven en registry.py.
Los imports públicos se re-exportan desde registry.py para no romper código
existente.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import ClassVar, Literal


CatalogLevel = Literal[
    "category_group", "category_type", "category_subtype",
]
MainLevel = Literal[
    "primary", "secondary", "relational",
]
CollectionLevel = Literal[
    "primary", "secondary", "relational",
    "category_group", "category_type", "category_subtype",
]


# ---------------------------------------------------------------------------
# Typed filter declarations (used in CollectionSchema.all_filters)
# ---------------------------------------------------------------------------

@dataclass
class FilterRef:
    """
    Referencia a un FilterGroup existente por key_name.
    Usado en CollectionSchema.all_filters.
    """
    filter_name: str
    hidden: bool = False


@dataclass
class ComponentFilter:
    """
    Filtro renderizado como componente Vue en el dashboard.
    Usado en CollectionSchema.all_filters.
    """
    title: str
    component: str
    field: str
    hidden: bool = False
    options: list | None = None        # para OnlyByFilter
    custom_options: list | None = None

def filter_to_dict(f: FilterRef | ComponentFilter) -> dict:
    """Serialize a filter dataclass to a plain dict, omitting None values."""
    return {k: v for k, v in asdict(f).items() if v is not None}


# ---------------------------------------------------------------------------
# BaseSchema — shared by CatalogSchema and CollectionSchema
# ---------------------------------------------------------------------------

class BaseSchema:
    """
    Mixin de tipado puro. Contiene solo los atributos genuinamente
    compartidos entre CatalogSchema y CollectionSchema.
    No tiene lógica propia — toda la lógica vive en los registries.
    """
    model: type = None
    level: str = None           # tipo estricto definido en cada subclase
    name: str = None            # fallback: model._meta.verbose_name
    plural_name: str = None     # fallback: model._meta.verbose_name_plural
    can_merge: bool = False
    can_massive_edit: bool = False
    sort_fields: list = []
    cat_params: dict = {}
    viewset_class: type | None = None


# ---------------------------------------------------------------------------
# CatalogSchema — category_group / category_type / category_subtype
# ---------------------------------------------------------------------------

class CatalogSchema(BaseSchema):
    """
    Declaración de una colección de tipo catálogo (category_*).

    Genera un ViewSet automáticamente para los patrones 1-3.
    Usa `viewset_class` para override manual (patrón 4).
    Puede declarar su FilterGroup simple con `filter_group_key`.
    """

    level: CatalogLevel = None

    # --- UI metadata --------------------------------------------------------
    open_insertion: bool = None
    optional_category: bool = False

    # --- ViewSet generation -------------------------------------------------
    # base: "status" → BaseStatusViewSet
    #       "generic" → BaseGenericViewSet
    #       "viewset" → plain ModelViewSet
    #       or a class reference
    base: str = "status"

    # permission: "editor" → IsEditorOrCreateOrRead
    #             "admin"  → IsAdminOrReadOnly
    #             "any"    → AllowAny
    #             or a class reference
    permission: str = "editor"

    # count_fields: {"annotation_name": "related_field_or_path"}
    count_fields: dict = {}

    # filterset_fields: None = inherit from base; [] = disable
    filterset_fields: list | None = None

    # extra_mixins: inserted before base class in MRO
    extra_mixins: list = []

    # --- Serializers --------------------------------------------------------
    serializer_class: type | None = None
    full_serializer_class: type | None = None   # retrieve / create / update
    list_serializer_class: type | None = None   # list action

    # --- FilterGroup simple (single category level) -------------------------
    # Set filter_group_key to auto-generate a FilterGroup for this schema.
    # Only suitable when this schema is the sole category_subtype/type for
    # the group (no category_group / category_type siblings needed).
    filter_group_key: str | None = None       # key_name del FilterGroup
    filter_group_main: str | None = None      # "app-snake_name" colección principal
    filter_group_addl_config: dict = {}


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

class CollectionSchema(BaseSchema):
    """
    Declaración de una colección principal, secundaria o relacional.

    Siempre usa ViewSet manual — `viewset_class` es obligatorio.
    Alimenta el router principal via `collection_registry.register_routes()`.
    """

    level: MainLevel = None

    # --- UI metadata (exclusive to non-catalog collections) -----------------
    color: str = None
    icon: str = None
    all_filters: list = []     # List[FilterRef | ComponentFilter]
    xls_export: bool = False
    can_massive_delete: bool = False

    # When set, register_routes also registers {snake_name}_mini
    mini_viewset_class: type | None = None


# ---------------------------------------------------------------------------
# FilterGroupSchema — complex multi-level filter groups
# ---------------------------------------------------------------------------

class FilterGroupSchema:
    """
    Declaración de un FilterGroup que agrupa múltiples niveles de catálogo
    (category_group + category_type + category_subtype).

    Para grupos simples (solo category_subtype), usar `CatalogSchema.filter_group_key`
    en el schema correspondiente en lugar de esta clase.

    Se registra con `catalog_registry.register_filter_group`.
    """
    key_name: str = None
    name: str = None
    plural_name: str = None
    main_collection: str = None          # "app-snake_name"
    category_group: type | None = None   # modelo Django
    category_type: type | None = None    # modelo Django
    category_subtype: type | None = None # modelo Django
    addl_config: dict = {}
