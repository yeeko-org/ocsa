from api.export_blocks.base import ExportBlock


class ImpactExportBlock(ExportBlock):
    """Columnas y extractor para Impact en exportaciones XLSX.

    Requiere select_related: impact_type__impact_group, impact_subtype.
    """

    columns = [
        {"name": "ID", "width": 5, "field": "id"},
        {"name": "Descripción de la afectación", "width": 50,
         "field": "description"},
        {"name": "Grupo de afectación", "width": 15,
         "field": "impact_type__impact_group"},
        {"name": "Tipo de afectación", "width": 15,
         "field": "impact_type__name"},
        {"name": "Subtipo de afectación", "width": 30,
         "field": "impact_subtype__name"},
    ]

    @classmethod
    def extract(cls, obj) -> dict:
        from utils.universal import safe_attr
        return {
            "id": obj.id,
            "description": obj.description,
            "impact_type": {
                "impact_group": safe_attr(
                    obj, 'impact_type', 'impact_group', 'name'),
                "name": safe_attr(obj, 'impact_type', 'name'),
            },
            "impact_subtype": {
                "name": safe_attr(obj, 'impact_subtype', 'name'),
            },
        }