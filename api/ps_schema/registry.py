"""
Registries para CatalogSchema y CollectionSchema.

Las declaraciones de schema (CatalogSchema, CollectionSchema, FilterGroupSchema,
FilterRef, ComponentFilter) viven en ps_schema/schemas.py.
Este módulo contiene la lógica de registro, generación de ViewSets y routing.

All se re-exporta aquí para que los imports existentes no se rompan:

    from ps_schema.registry import catalog_registry, CatalogSchema
    from ps_schema.registry import collection_registry, CollectionSchema
    from ps_schema.registry import FilterRef, ComponentFilter
"""
from __future__ import annotations

from ps_schema import generate_serializer
from ps_schema.schemas import (  # noqa: F401 — re-exported for callers
    CatalogLevel, MainLevel, CollectionLevel,
    FilterRef, ComponentFilter, filter_to_dict,
    BaseSchema, CatalogSchema, CollectionSchema, FilterGroupSchema,
)
from utils.universal import camel_to_snake


# ---------------------------------------------------------------------------
# Field metadata helper
# ---------------------------------------------------------------------------

def _model_fields(model_cls: type) -> list[dict]:
    """
    Return field metadata for a Django model class.
    Computes from model._meta — no DB queries, no cache needed.
    Adapted from the old InitCollections.field_of_models.
    """
    from django.db.models import CharField, TextField, IntegerField

    result = []
    for field in model_cls._meta.get_fields(
            include_parents=False, include_hidden=False):
        relation_type = "simple"
        is_primary_key = False
        if field.one_to_many:
            relation_type = "one_to_many"
        elif field.is_relation:
            if field.many_to_many:
                relation_type = "many_to_many"
            elif field.one_to_one:
                relation_type = "one_to_one"
            else:
                relation_type = "relation"
        else:
            is_primary_key = field.primary_key

        field_type = "unknown"
        width = 100
        is_string = is_char = False
        if isinstance(field, TextField):
            field_type, width, is_string = "text", 200, True
        if isinstance(field, CharField):
            field_type, width, is_string, is_char = "char", 150, True, True
        if isinstance(field, IntegerField):
            field_type, width = "integer", 80

        entry: dict = {
            "name": field.name,
            "real_name": f"{field.name}{'_id' if field.is_relation else ''}",
            "primary_key": is_primary_key,
            "relation_type": relation_type,
            "field_type": field_type,
            "is_string": is_string,
            "is_massive": False,
            "is_editable": True,
            "width": width,
            "null": field.null,
        }
        try:
            entry["verbose_name"] = field.verbose_name
        except AttributeError:
            pass
        try:
            if type(field.default) in [str, int, bool]:
                entry["default"] = field.default
        except AttributeError:
            pass
        if is_char:
            entry["max_length"] = field.max_length
        if field.is_relation:
            try:
                entry["related_name"] = field.related_query_name()
            except TypeError:
                pass
            try:
                meta = field.related_model._meta
                entry["related_snake_name"] = camel_to_snake(meta.object_name)
                entry["related_model"] = meta.object_name
                entry["related_app_label"] = meta.app_label
            except AttributeError:
                pass
        result.append(entry)
    return result


# ---------------------------------------------------------------------------
# Internal factory (CatalogSchema only)
# ---------------------------------------------------------------------------

def _generate_viewset(schema_cls: type[CatalogSchema]) -> type:
    """
    Generate a ModelViewSet subclass from a CatalogSchema declaration.
    Handles patterns 1-3 (simple, count+filter, two-serializer variants).
    """
    from django.db.models import Count
    from rest_framework import viewsets, permissions as drf_permissions
    from api.views.common_views import BaseStatusViewSet, BaseGenericViewSet
    from api.permissions import IsEditorOrCreateOrRead, IsAdminOrReadOnly

    base_map = {
        "status": BaseStatusViewSet,
        "generic": BaseGenericViewSet,
        "viewset": viewsets.ModelViewSet,
    }
    base = schema_cls.base
    base_cls = base if isinstance(base, type) else base_map[base]

    perm_map = {
        "editor": IsEditorOrCreateOrRead,
        "admin": IsAdminOrReadOnly,
        "any": drf_permissions.AllowAny,
    }
    perm = schema_cls.permission
    perm_cls = perm if isinstance(perm, type) else perm_map[perm]

    qs = schema_cls.model.objects.all()
    if schema_cls.count_fields:
        for ann_name, related_path in schema_cls.count_fields.items():
            qs = qs.annotate(**{ann_name: Count(related_path, distinct=True)})
        qs = qs.distinct()

    default_ser = schema_cls.serializer_class or generate_serializer(
        schema_cls.model, schema_cls.count_fields)
    full_ser = schema_cls.full_serializer_class
    list_ser = schema_cls.list_serializer_class

    attrs: dict = {
        'queryset': qs,
        'serializer_class': default_ser,
        'permission_classes': [perm_cls],
    }
    if schema_cls.filterset_fields is not None:
        attrs['filterset_fields'] = schema_cls.filterset_fields

    if full_ser or list_ser:
        def get_serializer_class(self,
                                 _full=full_ser,
                                 _list=list_ser,
                                 _default=default_ser):
            if _full and self.action in [
                    'retrieve', 'create', 'update', 'partial_update']:
                return _full
            if _list and self.action == 'list':
                return _list
            return _default
        attrs['get_serializer_class'] = get_serializer_class

    bases = tuple(schema_cls.extra_mixins) + (base_cls,)
    return type(f'{schema_cls.model.__name__}AutoViewSet', bases, attrs)


def _model_collection_key(model: type) -> str:
    return camel_to_snake(model._meta.object_name)


def _base_collection_dict(
    snake_name: str, schema_cls: type[BaseSchema],
) -> dict:
    """
    Campos comunes a CatalogRegistry y CollectionRegistry
    en iter_collection_data.  Cada registry agrega los suyos.
    """
    meta = schema_cls.model._meta
    return {
        'app_label': meta.app_label,
        'snake_name': snake_name,
        'model_name': meta.object_name,
        'name': schema_cls.name or meta.verbose_name,
        'plural_name': (
            schema_cls.plural_name or meta.verbose_name_plural),
        'level': schema_cls.level,
        'cat_params': schema_cls.cat_params,
        'sort_fields': schema_cls.sort_fields,
        'extra_massive_edit_fields': schema_cls.extra_massive_edit_fields,
    }


# ---------------------------------------------------------------------------
# CatalogRegistry
# ---------------------------------------------------------------------------

class CatalogRegistry:
    """
    Registry para CatalogSchema (category_*) y FilterGroupSchema.

    Provee generación y registro de ViewSets en el router de catálogos,
    dump de catálogos para CatalogsView, y metadata para InitCollections /
    InitFilterGroups.
    """

    def __init__(self) -> None:
        self._schemas: dict[str, type[CatalogSchema]] = {}
        self._filter_groups: dict[str, type[FilterGroupSchema]] = {}

    def register(
            self, schema_cls: type[CatalogSchema]) -> type[CatalogSchema]:
        """Decorator to register a CatalogSchema subclass."""
        if schema_cls.model is None:
            raise ValueError(f"{schema_cls.__name__}: 'model' is required")
        if schema_cls.level is None and schema_cls.viewset_class is None:
            raise ValueError(
                f"{schema_cls.__name__}: 'level' is required "
                f"(or set viewset_class for manual ViewSet)")
        snake_name = camel_to_snake(schema_cls.model.__name__)
        self._schemas[snake_name] = schema_cls
        return schema_cls

    def register_filter_group(
            self,
            schema_cls: type[FilterGroupSchema]) -> type[FilterGroupSchema]:
        """Decorator to register a FilterGroupSchema subclass."""
        if schema_cls.key_name is None:
            raise ValueError(f"{schema_cls.__name__}: 'key_name' is required")
        self._filter_groups[schema_cls.key_name] = schema_cls
        return schema_cls

    def get_viewset(self, snake_name: str) -> type:
        """Return the ViewSet class for a registered snake_name."""
        schema_cls = self._schemas[snake_name]
        if schema_cls.viewset_class:
            return schema_cls.viewset_class
        return _generate_viewset(schema_cls)

    def register_routes(self, router) -> None:
        """Register all catalog schemas into a DRF router."""
        for snake_name in self._schemas:
            viewset = self.get_viewset(snake_name)
            router.register(
                snake_name, viewset, basename=f'catalog_{snake_name}')

    def get_catalog_dump(self) -> dict:
        """
        Return {snake_name: serialized_list} for every registered schema.
        Plain model fields only (no count annotations) — for dropdown catalogs.
        """
        result = {}
        for snake_name, schema_cls in self._schemas.items():
            ser_class = generate_serializer(schema_cls.model)
            result[snake_name] = ser_class(
                schema_cls.model.objects.all(), many=True).data
        return result

    def iter_collection_data(self):
        """Yield (app_label, collection_dict) for InitCollections."""
        for snake_name, schema_cls in self._schemas.items():
            data = {
                **_base_collection_dict(snake_name, schema_cls),
                'icon': None,
                'color': None,
                'open_insertion': schema_cls.open_insertion,
                'optional_category': schema_cls.optional_category,
                'available_actions': [
                    a for a, flag in (
                        ("merge", schema_cls.can_merge),
                        ("massive_edit", schema_cls.can_massive_edit),
                    ) if flag
                ],
                'xls_export': False,
                'all_filters': [],
            }
            yield data['app_label'], data

    def get_collections_data(self) -> list[dict]:
        """
        Schema data + runtime field metadata.
        Catalog collections have no DB-editable fields — no overrides needed.
        """
        result = []
        for _app, data in self.iter_collection_data():
            data['fields'] = _model_fields(
                self._schemas[data['snake_name']].model)
            result.append(data)
        return result

    def iter_filter_group_data(self):
        """
        Yield filter group dicts for InitFilterGroups, combining:
        1. Explicit FilterGroupSchema registrations (complex multi-level groups)
        2. CatalogSchema entries with filter_group_key set (simple groups)
        """
        for key_name, schema_cls in self._filter_groups.items():
            group: dict = {
                'key_name': key_name,
                'name': schema_cls.name or key_name,
                'plural_name': schema_cls.plural_name or key_name,
                'main_collection': schema_cls.main_collection,
                'addl_config': schema_cls.addl_config,
            }
            if schema_cls.category_group:
                group['category_group'] = _model_collection_key(
                    schema_cls.category_group)
            if schema_cls.category_type:
                group['category_type'] = _model_collection_key(
                    schema_cls.category_type)
            if schema_cls.category_subtype:
                group['category_subtype'] = _model_collection_key(
                    schema_cls.category_subtype)
            yield group

        for snake_name, schema_cls in self._schemas.items():
            if not schema_cls.filter_group_key:
                continue
            model = schema_cls.model
            meta = model._meta
            yield {
                'key_name': schema_cls.filter_group_key,
                'name': schema_cls.name or meta.verbose_name,
                'plural_name': (
                    schema_cls.plural_name or meta.verbose_name_plural),
                'category_subtype': snake_name,
                'addl_config': schema_cls.filter_group_addl_config,
            }


# ---------------------------------------------------------------------------
# CollectionRegistry
# ---------------------------------------------------------------------------

class CollectionRegistry:
    """
    Registry para CollectionSchema (primary / secondary / relational).

    No genera ViewSets — todos son manuales (viewset_class obligatorio).
    Provee registro de rutas en el router principal (`api/urls.py`) y
    metadata de colecciones para InitCollections.
    """

    def __init__(self) -> None:
        self._schemas: dict[str, type[CollectionSchema]] = {}

    def register(
            self,
            schema_cls: type[CollectionSchema]) -> type[CollectionSchema]:
        """Decorator to register a CollectionSchema subclass."""
        if schema_cls.model is None:
            raise ValueError(f"{schema_cls.__name__}: 'model' is required")
        if schema_cls.viewset_class is None:
            raise ValueError(
                f"{schema_cls.__name__}: 'viewset_class' is required "
                f"for CollectionSchema (no auto-generation)")
        snake_name = camel_to_snake(schema_cls.model.__name__)
        self._schemas[snake_name] = schema_cls
        return schema_cls

    def register_routes(self, router) -> None:
        """Register all CollectionSchema viewsets into a DRF router.

        Cuando un schema define ``xls_export_class``, inyecta
        ``ExportActionMixin`` en el ViewSet dinámicamente para
        que la action ``export_xls`` se registre vía el router.
        """
        for snake_name, schema_cls in self._schemas.items():
            viewset_cls = self._with_export_mixin(schema_cls)
            router.register(
                snake_name, viewset_cls, basename=snake_name)
            if mini_class := schema_cls.mini_viewset_class:
                endpoint_name = f'{snake_name}_mini'
                router.register(
                    endpoint_name, mini_class, basename=endpoint_name)

    @staticmethod
    def _with_export_mixin(
        schema_cls: type,
    ) -> type:
        """Inyecta ExportActionMixin si el schema tiene export.

        Crea una subclase dinámica que hereda del mixin +
        ViewSet original, con ``xls_export_class`` configurado.
        """
        export_cls = schema_cls.xls_export_class
        if export_cls is None:
            return schema_cls.viewset_class

        from yeeko_xlsx_export import ExportActionMixin

        viewset_cls = schema_cls.viewset_class
        return type(
            f"{viewset_cls.__name__}Export",
            (ExportActionMixin, viewset_cls),
            {"xls_export_class": export_cls},
        )

    def iter_collection_data(self):
        """Yield (app_label, collection_dict) for InitCollections."""
        for snake_name, schema_cls in self._schemas.items():
            data = {
                **_base_collection_dict(snake_name, schema_cls),
                'icon': schema_cls.icon,
                'color': schema_cls.color,
                'open_insertion': None,
                'optional_category': False,
                'available_actions': [
                    a for a, flag in (
                        ("merge", schema_cls.can_merge),
                        ("massive_edit", schema_cls.can_massive_edit),
                        ("massive_delete",
                         schema_cls.can_massive_delete),
                    ) if flag
                ],
                'xls_export': (
                    schema_cls.xls_export_class is not None
                    or schema_cls.xls_export
                ),
                'all_filters': [
                    filter_to_dict(f)
                    for f in schema_cls.all_filters],
            }
            yield data['app_label'], data

    def get_collections_data(self) -> list[dict]:
        """
        Schema data + DB overrides (order, icon, color, help_text,
        description) + runtime field metadata.
        """
        from ps_schema.models import Collection  # lazy — avoids circular import
        db_overrides = {
            c.snake_name: {
                'order': c.order,
                'icon': c.icon,
                'color': c.color,
                'help_text': c.help_text,
                'description': c.description,
            }
            for c in Collection.objects.all()
        }
        result = []
        for _app, data in self.iter_collection_data():
            snake = data['snake_name']
            overrides = db_overrides.get(snake, {})
            merged = {
                **data,
                **{k: v for k, v in overrides.items() if v is not None},
            }
            merged['fields'] = _model_fields(self._schemas[snake].model)
            result.append(merged)
        return result


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------

catalog_registry = CatalogRegistry()
collection_registry = CollectionRegistry()
