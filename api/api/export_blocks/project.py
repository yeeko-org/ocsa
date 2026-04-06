from project.models import Conflict, Project
from yeeko_xlsx_export import (
    CollectColumn, FkColumn, Include, ModelExport, XlsColumn,
)
from api.export_blocks.conditions import (
    expand_project, expand_project_auth, is_authenticated,
)
from api.export_blocks.location import LocationBlock


class ConflictMiniBlock(ModelExport):
    """Columnas mínimas de Conflicto, reutilizable vía Include."""

    model = Conflict
    columns = [
        XlsColumn("id", title="ID de conflicto"),
        XlsColumn("name", title="Nombre de conflicto", width=30),
    ]


class ProjectMiniBlock(ModelExport):
    """Columnas mínimas de Proyecto, reutilizable vía Include."""

    model = Project
    columns = [
        XlsColumn("id", title="ID de proyecto"),
        XlsColumn("name", title="Nombre de proyecto", width=40),
    ]


class ProjectExpandBlock(ModelExport):
    """Campos extra de Proyecto, activados con ?expand_project=1.

    Pensado para incluirse después de ProjectMiniBlock en exports
    que llegan al proyecto vía MentionBlock (Event, Impact,
    Participant). Cada columna lleva condition para que solo
    aparezcan cuando el frontend lo solicita explícitamente.
    """

    model = Project
    columns = [
        XlsColumn(
            "is_grouper",
            condition=expand_project,
        ),
        FkColumn(
            "parent_project", "id",
            title="ID de proyecto agrupador",
            condition=expand_project,
        ),
        FkColumn(
            "parent_project", "name",
            title="Nombre de proyecto agrupador",
            width=30,
            condition=expand_project,
        ),
        CollectColumn(
            "megaproject_type__extractivism_types", "name",
            title="Tipos de extractivismo",
            width=25,
            condition=expand_project,
        ),
        FkColumn(
            "megaproject_type", "name",
            title="Tipo de megaproyecto",
            width=20,
            condition=expand_project,
        ),
        FkColumn(
            "status_location", "public_name",
            title="Status de ubicación",
            width=15,
            condition=expand_project_auth,
        ),
    ]


class ProjectExport(ModelExport):
    """Exportación completa de Proyectos.

    Incluye datos propios, proyecto agrupador, conflicto,
    tipo de megaproyecto, conteo/rango de notas y ubicación
    principal (vía anotaciones Subquery).
    """

    model = Project
    export_name = "Exportación de Proyectos"
    columns = [
        XlsColumn("id"),
        XlsColumn("name", width=35),
        XlsColumn("alternative_name", width=25),
        XlsColumn("description", width=40),
        Include(ConflictMiniBlock, through="conflict"),
        XlsColumn("is_grouper"),
        FkColumn(
            "parent_project", "id",
            title="ID de proyecto agrupador",
        ),
        FkColumn(
            "parent_project", "name",
            title="Nombre de proyecto agrupador",
            width=30,
        ),
        CollectColumn(
            "megaproject_type__extractivism_types", "name",
            title="Tipos de extractivismo",
            width=25,
        ),
        FkColumn(
            "megaproject_type", "name",
            title="Tipo de megaproyecto",
            width=20,
        ),
        FkColumn(
            "status_location", "public_name",
            title="Status de ubicación",
            width=15,
            condition=is_authenticated,
        ),
        Include(LocationBlock),
        CollectColumn(
            "mentions__note", "date",
            title="Número de notas",
            operation="count",
        ),
        CollectColumn(
            "mentions__note", "date",
            title="Primera nota",
            operation="min",
        ),
        CollectColumn(
            "mentions__note", "date",
            title="Última nota",
            operation="max",
        ),
        FkColumn(
            "status_validation", "public_name",
            title="Status de validación",
            width=15,
            condition=is_authenticated,
        ),
    ]

    def get_annotations(self) -> dict:
        return LocationBlock.build_annotations("project")
