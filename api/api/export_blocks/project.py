from project.models import Conflict, Project
from api.export_blocks.base import ExportBlock


class ConflictMiniExportBlock(ExportBlock):
    """Columnas y extractor mínimo para Conflict en exportaciones XLSX."""

    columns = [
        {"name": "ID de conflicto", "width": 5, "field": "id"},
        {"name": "Nombre de conflicto", "width": 30, "field": "name"},
    ]

    @classmethod
    def extract(cls, conflict: Conflict | None) -> dict:
        from utils.universal import safe_attr
        return {
            "id": safe_attr(conflict, 'id'),
            "name": safe_attr(conflict, 'name'),
        }


class ProjectMiniExportBlock(ExportBlock):
    """Columnas y extractor mínimo para Project en exportaciones XLSX."""

    columns = [
        {"name": "ID de proyecto", "width": 5, "field": "id"},
        {"name": "Nombre de proyecto", "width": 40, "field": "name"},
    ]

    @classmethod
    def extract(cls, project: Project | None) -> dict:
        from utils.universal import safe_attr
        return {
            "id": safe_attr(project, 'id'),
            "name": safe_attr(project, 'name'),
        }