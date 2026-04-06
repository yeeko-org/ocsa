from space_time.models import Location
from yeeko_xlsx_export import ModelExport, XlsColumn


class LocationBlock(ModelExport):
    """Bloque de ubicación principal — lee de anotaciones Subquery.

    Los valores provienen de anotaciones en el queryset padre, no de
    FK traversal directo. Las annotation keys usan ``_`` (no ``__``)
    para evitar que resolve_field_path las interprete como paths ORM.

    Uso en un export::

        class MyExport(ModelExport):
            columns = [
                ...,
                Include(LocationBlock),  # sin through
            ]

            def get_annotations(self) -> dict:
                return LocationBlock.build_annotations("event")
    """

    model = Location

    # Mapeo: annotation_key → path dentro de Location para Subquery
    _annotation_sources: dict[str, str] = {
        "location_id": "id",
        "state_inegi_code": "state__inegi_code",
        "state_short_name": "state__short_name",
        "municipality_inegi_code": "municipality__inegi_code",
        "municipality_name": "municipality__name",
        "locality_inegi_code": "locality__inegi_code",
        "locality_name": "locality__name",
        "loc_latitude": "latitude",
        "loc_longitude": "longitude",
    }

    columns = [
        XlsColumn(
            "location_id",
            title="ID de ubicación principal",
        ),
        XlsColumn(
            "state_inegi_code",
            title="ID de Entidad", width=4,
        ),
        XlsColumn(
            "state_short_name",
            title="Entidad", width=25,
        ),
        XlsColumn(
            "municipality_inegi_code",
            title="ID de Municipio", width=4,
        ),
        XlsColumn(
            "municipality_name",
            title="Municipio", width=25,
        ),
        XlsColumn(
            "locality_inegi_code",
            title="ID de Localidad", width=4,
        ),
        XlsColumn(
            "locality_name",
            title="Localidad", width=25,
        ),
        XlsColumn(
            "loc_latitude",
            title="Latitud", width=12,
        ),
        XlsColumn(
            "loc_longitude",
            title="Longitud", width=12,
        ),
    ]

    @classmethod
    def build_annotations(
        cls,
        target: str,
        outer_ref: str = "id",
        prefix: str = "",
    ) -> dict:
        """Genera anotaciones Subquery para la ubicación principal.

        Selecciona la Location con mayor prioridad de status_location
        y extrae sus campos como anotaciones planas del queryset padre.

        Args:
            target: FK en Location que apunta a la entidad padre
                (``"event"``, ``"impact"``, ``"project"``).
            outer_ref: campo del modelo raíz del queryset que se
                usa en ``OuterRef``. Default ``"id"`` (el modelo
                raíz ES la entidad). Para contextos anidados usar
                el path hasta el id de la entidad, e.g.
                ``"mention__project_id"``.
            prefix: prefijo para los annotation keys, útil cuando
                el export ya tiene un ``LocationBlock`` propio y
                se necesita evitar colisiones (e.g. ``"proj_"``).
        """
        from django.db.models import OuterRef, Subquery

        query_loc = {target: OuterRef(outer_ref)}
        max_priority = (
            Location.objects
            .filter(**query_loc)
            .order_by("-status_location__priority")
        )
        return {
            f"{prefix}{ann_key}": Subquery(
                max_priority.values(source)[:1],
            )
            for ann_key, source
            in cls._annotation_sources.items()
        }


class ProjectLocationBlock(ModelExport):
    """Ubicación principal del proyecto — annotations prefijadas.

    Se incluye a nivel raíz del Export (sin ``through``) porque
    las annotations viven en el objeto raíz del queryset, no en
    el objeto Project relacionado.

    La visibilidad se controla con
    ``Include(..., condition=expand_project)``, no en cada
    columna individual.

    Uso en un export::

        class EventExport(ModelExport):
            columns = [
                ...,
                Include(
                    ProjectLocationBlock,
                    condition=expand_project,
                ),
            ]

            def get_annotations(self) -> dict:
                return {
                    **LocationBlock.build_annotations("event"),
                    **LocationBlock.build_annotations(
                        "project",
                        outer_ref="mention__project_id",
                        prefix="proj_",
                    ),
                }
    """

    model = Location
    columns = [
        XlsColumn(
            "proj_location_id",
            title="ID de ubicación del proyecto",
        ),
        XlsColumn(
            "proj_state_inegi_code",
            title="ID de Entidad del proyecto", width=4,
        ),
        XlsColumn(
            "proj_state_short_name",
            title="Entidad del proyecto", width=25,
        ),
        XlsColumn(
            "proj_municipality_inegi_code",
            title="ID de Municipio del proyecto", width=4,
        ),
        XlsColumn(
            "proj_municipality_name",
            title="Municipio del proyecto", width=25,
        ),
        XlsColumn(
            "proj_locality_inegi_code",
            title="ID de Localidad del proyecto", width=4,
        ),
        XlsColumn(
            "proj_locality_name",
            title="Localidad del proyecto", width=25,
        ),
        XlsColumn(
            "proj_loc_latitude",
            title="Latitud del proyecto", width=12,
        ),
        XlsColumn(
            "proj_loc_longitude",
            title="Longitud del proyecto", width=12,
        ),
    ]
