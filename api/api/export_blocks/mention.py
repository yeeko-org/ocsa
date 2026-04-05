from api.export_blocks.base import ExportBlock
from api.export_blocks.project import (
    ProjectMiniExportBlock, ConflictMiniExportBlock)
from source.models import Note


class NoteExportBlock(ExportBlock):
    """
    Requiere select_related: source.
    """

    columns = [
        {"name": "ID de nota", "width": 5, "field": "id"},
        {"name": "Fecha de nota", "width": 10, "field": "date"},
        {"name": "Título de nota", "width": 40, "field": "title"},
        {"name": "Medio de la nota", "width": 15, "field": "source"},
    ]

    @classmethod
    def extract(cls, note: Note) -> dict:
        from utils.universal import safe_attr
        return {
            "id": note.id,
            "date": str(note.date),
            "title": note.title,
            "source": safe_attr(note, 'source', 'name'),
        }


class MentionExportBlock(ExportBlock):
    """Columnas y extractor para Mention en exportaciones XLSX.

    Se usa SIN preset en xls_attrs; los fields resultantes incluyen los
    prefijos mention__note__, mention__project__ y conflict__ derivados
    de la composición de los sub-bloques.
    Requiere select_related: mention__note__source,
                             mention__project__conflict.
    """

    columns = [
        *NoteExportBlock.prefixed("mention__note"),
        *ProjectMiniExportBlock.prefixed("mention__project"),
        *ConflictMiniExportBlock.prefixed("conflict"),
    ]

    @classmethod
    def extract(cls, obj) -> dict:
        """Extrae mention de cualquier objeto con FK .mention.

        Devuelve claves de primer nivel 'mention' y 'conflict' para el
        traversal de ExportXlsMixin (sin preset).
        """
        from utils.universal import safe_attr
        mention = obj.mention
        project = mention.project
        conflict = safe_attr(project, 'conflict')
        return {
            "mention": {
                "note": NoteExportBlock.extract(mention.note),
                "project": ProjectMiniExportBlock.extract(project),
            },
            "conflict": ConflictMiniExportBlock.extract(conflict),
        }


# Legacy — se eliminará cuando todos los ViewSets usen MentionExportBlock
xlsx_mention_group = MentionExportBlock.columns


def extract_mention(obj) -> dict:
    """Legacy wrapper — usar MentionExportBlock.extract en código nuevo."""
    return MentionExportBlock.extract(obj)

