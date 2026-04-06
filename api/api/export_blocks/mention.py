from source.models import Mention, Note
from yeeko_xlsx_export import ModelExport, XlsColumn, FkColumn, Include
from api.export_blocks.conditions import expand_project
from api.export_blocks.project import (
    ConflictMiniBlock, ProjectExpandBlock, ProjectMiniBlock,
)


class NoteBlock(ModelExport):
    """Columnas base de Nota, reutilizable vía Include."""

    model = Note
    columns = [
        XlsColumn("id", title="ID de nota"),
        XlsColumn("date", title="Fecha de nota"),
        XlsColumn("title", title="Título de nota", width=40),
        FkColumn(
            "source", "name",
            title="Medio de la nota",
        ),
    ]


class MentionBlock(ModelExport):
    """Bloque de Mención: compone Nota, Proyecto y Conflicto.

    Usado como Include(MentionBlock, through="mention") en exports
    cuyo modelo tiene FK a Mention.
    """

    model = Mention
    columns = [
        Include(NoteBlock, through="note"),
        Include(ProjectMiniBlock, through="project"),
        Include(ProjectExpandBlock, through="project", condition=expand_project),
        Include(
            ConflictMiniBlock, through="project__conflict",
        ),
    ]

