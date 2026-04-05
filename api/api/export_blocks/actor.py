from actor.models import Actor
from api.export_blocks.base import ExportBlock


xlsx_actor_fields = [
    {
        "special_group": "actor",
    },
    {
        "name": "Número de notas",
        "width": 15,
        "field": "note_dates",
        "operation": "count"
    },
    {
        "name": "Primera nota",
        "width": 15,
        "field": "note_dates",
        "operation": "min"
    },
    {
        "name": "Status de validación",
        "width": 15,
        "field": "status_validation",
        "conditions": ["only_logged_in"]
    },
    {
        "name": "Última nota",
        "width": 15,
        "field": "note_dates",
        "operation": "max"
    }
]

class ActorExportBlock(ExportBlock):
    """Columnas y extractor para Actor en exportaciones XLSX.

    Requiere select_related: sector, indigenous_group, parent_actor.
    Requiere prefetch_related: belongs, countries.
    """

    columns = [
        {"name": "ID del Actor", "width": 5, "field": "id"},
        {"name": "Nombre del Actor", "width": 35, "field": "name"},
        {
            "name": "Nombres alternativos", "width": 25,
            "field": "alternative_names",
            "conditions": ["only_logged_in"],
        },
        {"name": "ID de actor agrupador", "width": 5,
         "field": "parent_actor__id"},
        {"name": "Nombre de actor agrupador", "width": 30,
         "field": "parent_actor__name"},
        {"name": "Sector", "width": 30, "field": "sector"},
        {"name": "Pertenencias (vulnerabilidades)", "width": 30,
         "field": "belongs"},
        {"name": "Grupo indígena", "width": 30, "field": "indigenous_group"},
        {
            "name": "Sexo", "width": 10, "field": "sex",
            "conditions": ["only_logged_in"],
        },
        {"name": "Paises origen", "width": 30, "field": "countries"},
    ]

    @classmethod
    def extract(cls, actor: Actor) -> dict:
        from utils.universal import safe_attr
        return {
            "id": actor.id,
            "name": actor.name,
            "alternative_names": actor.alternative_names,
            "parent_actor": {
                "id": actor.parent_actor_id,
                "name": safe_attr(actor, 'parent_actor', 'name'),
            },
            "sector": safe_attr(actor, 'sector', 'name'),
            "belongs": [b.name for b in actor.belongs.all()],
            "indigenous_group": safe_attr(actor, 'indigenous_group', 'name'),
            "sex": actor.sex,
            "countries": [c.name for c in actor.countries.all()],
        }



