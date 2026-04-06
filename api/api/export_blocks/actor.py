"""Bloques y export de Actor para exportación XLSX.

ActorBlock — bloque reutilizable (campos base del actor).
ActorExport — export completo con notas y status de validación.
"""
from actor.models import Actor
from api.export_blocks.conditions import is_authenticated
from yeeko_xlsx_export import (
    CollectColumn, FkColumn, Include, ModelExport, XlsColumn,
)


class ActorBlock(ModelExport):
    """Columnas base de Actor, reutilizable vía Include.

    Infiere automáticamente:
      select_related: parent_actor, sector, indigenous_group
      prefetch_related: belongs, countries
    """

    model = Actor
    columns = [
        XlsColumn("id", title="ID del Actor"),
        XlsColumn("name", title="Nombre del Actor", width=35),
        XlsColumn(
            "alternative_names",
            width=25,
            condition=is_authenticated,
        ),
        FkColumn(
            "parent_actor", "id",
            title="ID de actor agrupador",
        ),
        FkColumn(
            "parent_actor", "name",
            title="Nombre de actor agrupador",
        ),
        FkColumn(
            "sector", "name",
            title="Sector", width=30,
        ),
        CollectColumn(
            "belongs", "name",
            title="Pertenencias (vulnerabilidades)",
            width=30,
        ),
        FkColumn(
            "indigenous_group", "name",
            title="Grupo indígena", width=30,
        ),
        XlsColumn(
            "sex",
            title="Sexo",
            width=10,
            condition=is_authenticated,
        ),
        CollectColumn(
            "countries", "name",
            title="Paises origen",
            width=30,
        ),
    ]


class ActorExport(ModelExport):
    """Exportación completa de Actores.

    Incluye campos base (ActorBlock), conteo/rango de notas
    vía participants→mention→note, y status de validación.
    """

    model = Actor
    export_name = "Exportación de Actores"
    columns = [
        Include(ActorBlock),
        CollectColumn(
            "participants__mention__note", "date",
            title="Número de notas",
            operation="count",
        ),
        CollectColumn(
            "participants__mention__note", "date",
            title="Primera nota",
            operation="min",
        ),
        CollectColumn(
            "participants__mention__note", "date",
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

