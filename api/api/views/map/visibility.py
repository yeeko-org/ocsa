"""Criterio único de visibilidad pública del mapa (docs `adr-0022`).

Una **ubicación** es visible si su propio ``status_location`` es público
**y** la validación de su proyecto lo es. Un **proyecto** es visible si
tiene al menos una ubicación visible. De ahí se derivan las menciones y
las participaciones: son visibles cuando su proyecto lo es.

El ``status_location`` a nivel proyecto **no participa**: desde
`adr-0027` es un indicador derivado del dashboard, sin peso en los
filtros del mapa.

Todos los endpoints del mapa —geojson de pins, facetas, actores y
``project_map``— consumen estos helpers; ninguno conserva criterio
propio.
"""

from django.db.models import Exists, OuterRef, QuerySet

from space_time.models import Location

PUBLIC_LOCATION = {"status_location__is_public": True}


def visible_locations(queryset: QuerySet) -> QuerySet:
    """Ubicaciones públicas de proyectos con validación pública.

    El join a ``project`` descarta por sí solo las ubicaciones sin
    proyecto (las de evento o impacto), que nunca son pins del mapa.
    """
    return queryset.filter(
        project__status_validation__is_public=True, **PUBLIC_LOCATION)


def visible_projects(queryset: QuerySet, path: str = "") -> QuerySet:
    """Filtra por proyecto visible: validación pública + alguna
    ubicación pública.

    ``path`` es la ruta de lookup desde el modelo del queryset hasta
    ``Project`` (``""`` cuando el queryset ya es de ``Project``,
    ``"project"`` para ``Mention``, ``"mention__project"`` para
    ``Participant``). Se usa ``Exists`` en vez de un join a
    ``locations`` para no duplicar filas ni necesitar ``distinct``.
    """
    prefix = f"{path}__" if path else ""
    # La validación ya se comprueba fuera: la subconsulta solo pregunta
    # por el estatus de la ubicación, sin rehacer el join a proyecto.
    has_public_location = Exists(Location.objects.filter(
        project=OuterRef(f"{prefix}pk"), **PUBLIC_LOCATION))
    return queryset.filter(
        **{f"{prefix}status_validation__is_public": True}
    ).filter(has_public_location)


def visible_mentions(queryset: QuerySet, path: str = "") -> QuerySet:
    """Menciones de proyecto visible cuya nota es pública.

    El mismo criterio un escalón abajo: una faceta no puede contarse si
    su evidencia no se puede abrir en ``note_map``. ``path`` es la ruta
    de lookup hasta ``Mention`` (``""`` para ``Mention``, ``"mention"``
    para ``Participant``).
    """
    prefix = f"{path}__" if path else ""
    queryset = queryset.filter(
        **{f"{prefix}note__status_register__is_public": True})
    return visible_projects(queryset, f"{prefix}project")
