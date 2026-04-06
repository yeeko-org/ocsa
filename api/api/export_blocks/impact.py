"""Bloques y export de Impact para exportación XLSX.

ImpactBlock — bloque reutilizable (campos base de la afectación).
ImpactExport — export completo con mención, nota y ubicación.
"""
from impact.models import Impact
from api.export_blocks.location import LocationBlock, ProjectLocationBlock
from api.export_blocks.mention import MentionBlock
from yeeko_xlsx_export import (
    ModelExport, XlsColumn, FkColumn, Include,
)


class ImpactBlock(ModelExport):
    """Columnas base de Impact, reutilizable vía Include.
    """

    model = Impact
    columns = [
        XlsColumn("id"),
        XlsColumn("description", width=50),
        FkColumn(
            "impact_type", "impact_group__name",
            title="Grupo de afectación", width=15,
        ),
        FkColumn(
            "impact_type", "name",
            title="Tipo de afectación", width=15,
        ),
        FkColumn(
            "impact_subtype", "name",
            title="Subtipo de afectación", width=30,
        ),
    ]


class ImpactExport(ModelExport):
    """Exportación completa de Afectaciones.
    """

    model = Impact
    export_name = "Exportación de Afectaciones"
    columns = [
        Include(ImpactBlock),
        Include(MentionBlock, through="mention"),
        Include(LocationBlock),
        Include(ProjectLocationBlock),
    ]

    def get_annotations(self) -> dict:
        return {
            **LocationBlock.build_annotations("impact"),
            **LocationBlock.build_annotations(
                "project",
                outer_ref="mention__project_id",
                prefix="proj_",
            ),
        }