from ps_schema.registry import (
    catalog_registry, CatalogSchema,
    collection_registry, CollectionSchema, FilterRef, ComponentFilter,
    FilterGroupSchema,
)
from project.models import (
    ExtractivismType, StatusProject, MegaprojectType,
    Project, ProjectFile, Conflict,
)
from api.views.catalogs import StatusProjectViewSet, MegaprojectTypeViewSet


@catalog_registry.register
class ExtractivismTypeSchema(CatalogSchema):
    model = ExtractivismType
    level = "category_type"
    base = "generic"
    permission = "admin"
    count_fields = {"megaproject_types_count": "megaproject_types"}
    sort_fields = ['count', {'count': 'Cantidad de proyectos'}]


@catalog_registry.register
class StatusProjectSchema(CatalogSchema):
    model = StatusProject
    level = "category_subtype"
    open_insertion = True
    can_merge = True
    cat_params = {"select_component": "autocomplete"}
    viewset_class = StatusProjectViewSet
    filter_group_key = "status_projects"
    filter_group_addl_config = {"subtype_is_autocomplete": True}


@catalog_registry.register
class MegaprojectTypeSchema(CatalogSchema):
    model = MegaprojectType
    level = "category_subtype"
    open_insertion = True
    can_merge = True
    viewset_class = MegaprojectTypeViewSet


@catalog_registry.register_filter_group
class ProjectTypesFilterGroup(FilterGroupSchema):
    key_name = "project_types"
    name = "Clasificación de Proyecto"
    plural_name = "Clasificaciones de Proyecto"
    main_collection = "project-project"
    category_type = ExtractivismType
    category_subtype = MegaprojectType
    addl_config = {"subtype_is_autocomplete": True, "open_search": True}


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

from api.export_blocks.project import ProjectExport  # noqa: E402
from api.views.project import (  # noqa: E402
    ProjectViewSet, ProjectFileViewSet, ConflictViewSet, ProjectMiniViewSet)


@collection_registry.register
class ProjectSchema(CollectionSchema):
    model = Project
    level = "primary"
    viewset_class = ProjectViewSet
    mini_viewset_class = ProjectMiniViewSet
    icon = "factory"
    color = "purple"
    sort_fields = [
        'id', 'status_validation__order', 'name', 'status_location__order']
    can_merge = True
    can_massive_edit = True
    xls_export_class = ProjectExport
    extra_massive_edit_fields = ["conflict"]
    # status_location se deriva del mínimo de sus ubicaciones (adr-0027)
    read_only_fields = ["status_location"]
    all_filters = [
        FilterRef("project_types", can_massive_edit=True),
        FilterRef("states"),
        FilterRef("status_projects", hidden=True),
        FilterRef("impact_types", hidden=True),
        FilterRef("event_types", hidden=True),
        ComponentFilter(
            title="Es agrupador", field="is_grouper",
            component="TripleBooleanFilter", hidden=True),
        ComponentFilter(
            title="Editor", field="editor",
            component="UserSelect", hidden=True),
        ComponentFilter(
            title="Con ubicaciones", field="has_locations",
            component="TripleBooleanFilter", hidden=True),
        ComponentFilter(
            title="Ubicaciones marcadas en el mapa", field="geom_status",
            component="OnlyByFilter", hidden=True,
            custom_options=[
                {"plural_name": "Todas marcadas", "value": "all_geo"},
                {"plural_name": "Ninguna marcada", "value": "none_geo"},
                {"plural_name": "Solo algunas marcadas", "value": "mixed"},
            ]),
        ComponentFilter(
            title="Pendientes de ubicación", field="locations_pending",
            component="OnlyByFilter", hidden=True,
            description="Te muestra los proyectos con alguna ubicación "
                        "a la que todavía le falta algo para quedar "
                        "lista. Para ver en qué estatus va cada una, usa "
                        "el filtro de estatus de ubicación.",
            custom_options=[
                {"plural_name": "Sin marca en el mapa",
                 "value": "no_geometry",
                 "description": "Alguna de sus ubicaciones todavía no "
                                "está marcada en el mapa."},
                {"plural_name": "Sin municipio", "value": "no_municipality",
                 "description": "Alguna de sus ubicaciones está marcada en "
                                "el mapa, pero sin municipio anotado."},
                {"plural_name": "Completas sin aprobar",
                 "value": "complete_unapproved",
                 "description": "Alguna de sus ubicaciones tiene todos los "
                                "datos, pero nadie la ha aprobado."},
                {"plural_name": "Sin ninguna ubicación aprobada",
                 "value": "no_approved_location",
                 "description": "No puede aparecer en el mapa: no tiene "
                                "ubicaciones, o ninguna de ellas está "
                                "aprobada."},
                {"plural_name": "Alguno de los casos anteriores",
                 "value": "any_pending",
                 "description": "Junta en una sola lista los proyectos con "
                                "cualquiera de los pendientes de arriba."},
            ]),
        ComponentFilter(
            title="Conflictos", field="is_grouper",
            component="ConflictFilter", hidden=True),
    ]


@collection_registry.register
class ConflictSchema(CollectionSchema):
    model = Conflict
    level = "primary"
    viewset_class = ConflictViewSet
    mini_viewset_class = ConflictViewSet  # conflict_mini usa el mismo ViewSet
    icon = "local_fire_department"
    color = "pink"
    can_merge = True
    all_filters = [
        FilterRef("states", hidden=True),
        FilterRef("project_types", hidden=True),
        ComponentFilter(
            title="Tiene proyectos", field="has_projects",
            component="TripleBooleanFilter"),
    ]


@collection_registry.register
class ProjectFileSchema(CollectionSchema):
    model = ProjectFile
    level = "relational"
    viewset_class = ProjectFileViewSet