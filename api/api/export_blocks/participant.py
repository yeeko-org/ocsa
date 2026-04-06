"""Bloques y export de Participant para exportación XLSX.

ParticipantBlock — bloque reutilizable (campos base).
ParticipantExport — export completo con expansión 1→N
    (un participante con N involvements → N filas).
"""
from __future__ import annotations

from typing import Any

from actor.models import Participant
from api.export_blocks.actor import ActorBlock
from api.export_blocks.conditions import is_authenticated
from api.export_blocks.event import EventBlock
from api.export_blocks.location import LocationBlock, ProjectLocationBlock
from api.export_blocks.mention import MentionBlock
from yeeko_xlsx_export import (
    CollectColumn, Include, ModelExport, XlsColumn,
)


class ParticipantBlock(ModelExport):
    """Columnas base de Participant, reutilizable vía Include.

    Incluye datos del actor embebidos (ActorBlock through="actor")
    y campos M2M de tipos de participación e intereses resueltos
    con CollectColumn.

    Infiere automáticamente:
      select_related: actor → (delegado a ActorBlock)
      prefetch_related: participant_types, interests
    """

    model = Participant
    columns = [
        XlsColumn("id"),
        Include(ActorBlock, through="actor"),
        CollectColumn(
            "participant_types__participant_group", "name",
            title="Posición en el proyecto",
            width=20,
        ),
        CollectColumn(
            "participant_types", "name",
            title="Tipos de participación",
            width=20,
        ),
        CollectColumn(
            "interests__interest_subtype__interest_type__interest_group",
            "name",
            title="Grupo de interés",
            width=30,
            condition=is_authenticated,
        ),
        CollectColumn(
            "interests__interest_subtype"
            "__interest_type", "name",
            title="Tipo de interés",
            width=30,
            condition=is_authenticated,
        ),
        CollectColumn(
            "interests__interest_subtype", "name",
            title="Subtipo de interés",
            width=30,
            condition=is_authenticated,
        ),
        CollectColumn(
            "interests", "text",
            title="Descripción del interés",
            width=40,
        ),
    ]


class ParticipantExport(ModelExport):
    """Exportación completa de Participantes.

    Compone ParticipantBlock + EventBlock + MentionBlock.
    Cada participante se expande en N filas si tiene N
    involvements (patrón expand 1→N vía extract_row).

    Include(EventBlock, through="event") declara los headers;
    como Participant no tiene FK directa a Event, el framework
    llena con vacíos y extract_row los sobreescribe con los
    datos reales de cada involvement.
    """

    model = Participant
    export_name = "Participantes"
    columns = [
        XlsColumn(
            "mention_id", title="ID de mención",
        ),
        XlsColumn(
            "consecutive",
            title="Consecutivo", width=5,
        ),
        Include(ParticipantBlock),
        Include(EventBlock, through="event"),
        XlsColumn(
            "involved_role",
            title="Rol en el evento", width=20,
        ),
        Include(MentionBlock, through="mention"),
        Include(ProjectLocationBlock),
    ]
    extra_prefetch = [
        "involvements__event__event_type__event_group",
        "involvements__event__purpose",
        "involvements__involved_role",
    ]

    def get_annotations(self) -> dict[str, Any]:
        return LocationBlock.build_annotations(
            "project",
            outer_ref="mention__project_id",
            prefix="proj_",
        )

    def extract_row(
        self, obj: Any, request: Any = None,
    ) -> list[dict[str, Any]]:
        """Expansión 1→N: una fila por involvement.

        1. super() extrae participant + mention correctamente;
           event queda vacío (no hay FK directa).
        2. Por cada involvement, sobreescribimos consecutive,
           event__* e involved_role.
        3. Sin involvements → 1 fila con evento vacío.
        """
        base = super().extract_row(obj, request)
        involvements = list(obj.involvements.all())

        if not involvements:
            base["consecutive"] = 1
            base["involved_role"] = ""
            return [base]

        event_block = EventBlock()
        rows: list[dict[str, Any]] = []
        for i, inv in enumerate(involvements, start=1):
            row = {**base, "consecutive": i}
            event_data = event_block.extract_row(
                inv.event, request,
            )
            for key, value in event_data.items():
                row[f"event__{key}"] = value
            row["involved_role"] = (
                inv.involved_role.name
                if inv.involved_role else ""
            )
            rows.append(row)
        return rows
