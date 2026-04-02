---
name: manage-collections
description: >
  Create or edit CatalogSchema, CollectionSchema, and FilterGroupSchema in
  {app}/catalog_schema.py. Use when adding a new collection, catalog, or
  filter group, or modifying an existing one.
---

# manage-collections

## Architecture overview

Full attribute reference lives in `ps_schema/schemas.py`. Registry logic in
`ps_schema/registry.py`. This skill covers design decisions only.

| Level | Schema | Registry | Router |
|-------|--------|----------|--------|
| `category_group/type/subtype` | `CatalogSchema` | `catalog_registry` | `api/views/catalogs/urls.py` |
| `primary/secondary/relational` | `CollectionSchema` | `collection_registry` | `api/urls.py` |

Still registered manually in `api/urls.py`: `project_location`, `*_map`,
`collection`, `offline_task`.

---

## CatalogSchema — choosing a pattern

| Pattern | When | Key attributes |
|---------|------|----------------|
| **1 — Trivial** | Basic CRUD only | `model`, `level` |
| **2 — Count + filter** | Needs annotations or filters | `count_fields`, `filterset_fields` |
| **3 — Two serializers** | Different list vs retrieve | `list_serializer_class`, `full_serializer_class` |
| **4 — Override** | Custom logic, custom FilterSet | `viewset_class` |

```python
from ps_schema.registry import catalog_registry, CatalogSchema
from {app}.models import ModelA

@catalog_registry.register
class ModelASchema(CatalogSchema):
    model = ModelA
    level = "category_subtype"
    open_insertion = True
    can_merge = True
    count_fields = {"items_count": "related_field"}   # pattern 2
    filterset_fields = ["status_validation", "parent"]
    full_serializer_class = ModelAFullSerializer       # pattern 3
    # Simple FilterGroup (single category_subtype only):
    filter_group_key = "model_as"
    filter_group_main = "app-snake_name"
```

---

## CollectionSchema

`viewset_class` is required. `mini_viewset_class` auto-registers a
`{snake}_mini` endpoint when a lightweight ViewSet exists for selectors.

```python
from ps_schema.registry import (
    collection_registry, CollectionSchema, FilterRef, ComponentFilter)
from {app}.models import MyModel
from api.views.{app} import MyModelViewSet

@collection_registry.register
class MyModelSchema(CollectionSchema):
    model = MyModel
    level = "primary"
    viewset_class = MyModelViewSet
    mini_viewset_class = MyModelMiniViewSet  # optional
    icon = "factory"
    color = "purple"
    can_merge = True
    xls_export = True
    all_filters = [
        FilterRef("project_types"),
        FilterRef("states", hidden=True),
        ComponentFilter(
            title="Es agrupador", field="is_grouper",
            component="TripleBooleanFilter", hidden=True),
    ]
```

---

## ComponentFilter — available components

```python
ComponentFilter(title="Fechas", component="RangeDates", field="date")
ComponentFilter(title="Editor", field="editor", component="UserSelect", hidden=True)
ComponentFilter(title="Con archivos", field="has_files",
                component="TripleBooleanFilter", hidden=True)

# OnlyByFilter with fixed options:
ComponentFilter(title="Colección", field="only_by", component="OnlyByFilter",
                options=["project", "event", "impact"])

# OnlyByFilter with custom options:
ComponentFilter(title="Status", field="status", component="OnlyByFilter",
                custom_options=[
                    {"plural_name": "Faltan validar", "value": "to_validate"},
                    {"plural_name": "Validados", "value": "validated"},
                ])
```

---

## FilterGroupSchema — multi-level filter groups

Use when the group needs `category_type` + `category_subtype` (or also
`category_group`). For groups with only `category_subtype`, use
`filter_group_key` directly on the model's `CatalogSchema`.

```python
from ps_schema.registry import catalog_registry, FilterGroupSchema
from classify.models import SectorGroup, Sector

@catalog_registry.register_filter_group
class SectorsFilterGroup(FilterGroupSchema):
    key_name = "sectors"
    name = "Sector"
    plural_name = "Sectores"
    main_collection = "actor-actor"
    category_type = SectorGroup
    category_subtype = Sector
    addl_config = {"subtype_is_autocomplete": True, "open_search": True}
```

---

## Auto-discovery (new apps only)

If the app does not yet import its `catalog_schema` in `ready()`:

```python
# {app}/apps.py
def ready(self):
    import {app}.catalog_schema  # noqa
```