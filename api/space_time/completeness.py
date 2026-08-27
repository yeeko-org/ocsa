"""Pendientes de una `Location`: qué le falta para quedar lista.

Completa es un hecho verificable —entidad, municipio y geometría, donde
geometría es el par lat/lon o un geojson (adr-0024)—; el status de
ubicación lo mueve una persona. task-69 reformula la lectura de ese
criterio: en vez de tres cajones excluyentes, cada opción nombra un
encargo concreto y varias pueden caer sobre la misma ubicación.

Aprobada se define en un solo lugar (`approved_q`) y por la bandera
`is_public` del status, la misma con la que el mapa decide qué dibuja.

Las Q de este módulo se evalúan siempre sobre `Location`; a nivel de
proyecto se aplican con una subconsulta (`locations__in=...`) para que
las condiciones caigan sobre la misma ubicación y para no negar a
través de una relación múltiple.
"""

from __future__ import annotations

from django.db.models import Q

from project.models import Project
from space_time.geometry import has_geometry_q, no_geometry_q
from space_time.models import Location

NO_GEOMETRY = "no_geometry"
NO_MUNICIPALITY = "no_municipality"
COMPLETE_UNAPPROVED = "complete_unapproved"
NO_APPROVED_LOCATION = "no_approved_location"
ANY_PENDING = "any_pending"

LOCATION_OPTIONS = (NO_GEOMETRY, NO_MUNICIPALITY, COMPLETE_UNAPPROVED)


def with_project_q() -> Q:
    """Solo las ubicaciones de proyecto: son las únicas que se capturan."""
    return Q(project__isnull=False)


def complete_q() -> Q:
    """Entidad, municipio y geometría presentes."""
    return (
        Q(state__isnull=False)
        & Q(municipality__isnull=False)
        & has_geometry_q())


def approved_q() -> Q:
    """Ubicación aprobada, definición única del módulo (adr-0022).

    Aprobada y dibujable en el mapa son la misma pregunta, y la responde
    la bandera del status —la misma que `api/views/map/visibility.py`—,
    no una lista de nombres: quien agregue un status nuevo ajusta su
    `is_public` y no tiene que acordarse de este archivo.
    """
    return Q(status_location__is_public=True)


def unapproved_q() -> Q:
    """Negación de `approved_q`.

    El nulo se nombra aparte porque una comparación con NULL no es
    verdadera en SQL y el status de ubicación es opcional.
    """
    return (
        Q(status_location__isnull=True)
        | Q(status_location__is_public=False))


def location_pending_q(option: str) -> Q | None:
    """Q sobre `Location` de la opción pedida, o `None` si no existe."""
    if option == NO_GEOMETRY:
        condition = no_geometry_q()
    elif option == NO_MUNICIPALITY:
        condition = has_geometry_q() & Q(municipality__isnull=True)
    elif option == COMPLETE_UNAPPROVED:
        condition = complete_q() & unapproved_q()
    elif option == ANY_PENDING:
        condition = (
            no_geometry_q()
            | (has_geometry_q() & Q(municipality__isnull=True))
            | (complete_q() & unapproved_q()))
    else:
        return None
    return with_project_q() & condition


def no_approved_location_q() -> Q:
    """Proyectos sin ninguna ubicación aprobada, incluidos los que no
    tienen ninguna ubicación: en ambos casos el proyecto no se dibuja.

    La validación del proyecto no entra: se apila con su propio filtro.
    La negación cae sobre `pk`, no sobre `locations`: un `~Q` sobre la
    relación múltiple comparte el join cuando se combina con un OR y
    Django lo reancla a la ubicación unida, con lo que pasa a leerse
    como «alguna ubicación no aprobada».
    """
    approved = Location.objects.filter(approved_q())
    return ~Q(pk__in=Project.objects.filter(locations__in=approved))


def project_pending_q(option: str) -> Q | None:
    """Q sobre `Project` de la opción pedida, o `None` si no existe."""
    if option == NO_APPROVED_LOCATION:
        return no_approved_location_q()
    if option == ANY_PENDING:
        pending = Location.objects.filter(location_pending_q(ANY_PENDING))
        return Q(locations__in=pending) | no_approved_location_q()
    condition = location_pending_q(option)
    if condition is None:
        return None
    return Q(locations__in=Location.objects.filter(condition))
