"""Bloques y export de Event para exportación XLSX.

EventBlock — bloque reutilizable (columnas base del evento).
EventExport — export completo con mención, ubicación.
"""
from typing import Any

from event.models import Event
from yeeko_xlsx_export import (
    ModelExport, XlsColumn, FkColumn, Include,
)
from api.export_blocks.location import LocationBlock, ProjectLocationBlock
from api.export_blocks.mention import MentionBlock


class EventBlock(ModelExport):
    """Columnas base de Event, reutilizable vía Include.

    Infiere automáticamente:
      select_related: event_type, event_type__event_group, purpose
    """

    model = Event
    columns = [
        XlsColumn("id", title="ID del evento"),
        FkColumn(
            "event_type", "event_group__name",
            title="Grupo de evento", width=15,
        ),
        FkColumn(
            "event_type", "name",
            title="Tipo de evento", width=30,
        ),
        XlsColumn(
            "description",
            title="Descripción del evento", width=50,
        ),
        XlsColumn(
            "number_women",
            title="Mujeres víctimas", width=4,
        ),
        XlsColumn(
            "number_men",
            title="Hombres víctimas", width=4,
        ),
        XlsColumn(
            "number_mix",
            title="Personas víctimas", width=4,
        ),
        FkColumn(
            "purpose", "name",
            title="Intención del mecanismo", width=18,
        ),
    ]


class EventExport(ModelExport):
    """Exportación completa de Eventos.

    Compone EventBlock + MentionBlock (nota, proyecto, conflicto)
    + LocationBlock (ubicación principal vía anotaciones Subquery).
    """

    model = Event
    export_name = "Eventos"
    columns = [
        Include(EventBlock),
        Include(MentionBlock, through="mention"),
        Include(LocationBlock),
        Include(ProjectLocationBlock),
    ]

    def get_annotations(self) -> dict[str, Any]:
        return {
            **LocationBlock.build_annotations("event"),
            **LocationBlock.build_annotations(
                "project",
                outer_ref="mention__project_id",
                prefix="proj_",
            ),
        }
