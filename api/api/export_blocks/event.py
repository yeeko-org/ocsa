from api.export_blocks.base import ExportBlock
from utils.universal import safe_attr


class EventExportBlock(ExportBlock):
    """Columnas y extractor para Event en exportaciones XLSX.

    Requiere select_related: event_type__event_group, purpose.
    """

    columns = [
        {"name": "ID del evento", "width": 5, "field": "id"},
        {"name": "Grupo de evento", "width": 15, "field": "event_type__event_group"},
        {"name": "Tipo de evento", "width": 30, "field": "event_type__name"},
        {"name": "Descripción del evento", "width": 50, "field": "description"},
        {"name": "Mujeres víctimas", "width": 4, "field": "number_women"},
        {"name": "Hombres víctimas", "width": 4, "field": "number_men"},
        {"name": "Personas víctimas", "width": 4, "field": "number_mix"},
        {"name": "Intención del mecanismo", "width": 18, "field": "purpose"},
    ]

    @classmethod
    def extract(cls, obj) -> dict:
        """Extrae campos de Event para exportación XLSX."""
        return {
            "id": obj.id,
            "event_type": {
                "event_group": safe_attr(
                    obj, 'event_type', 'event_group', 'name'),
                "name": safe_attr(obj, 'event_type', 'name'),
            },
            "description": obj.description,
            "number_women": obj.number_women,
            "number_men": obj.number_men,
            "number_mix": obj.number_mix,
            "purpose": safe_attr(obj, 'purpose', 'name'),
        }