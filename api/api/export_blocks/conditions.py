"""Conditions reutilizables para columnas de exportación XLSX.

Cada función recibe un ``request`` y retorna ``bool``.
Se pasan como ``condition=is_authenticated`` en XlsColumn.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rest_framework.request import Request


def is_authenticated(request: Request) -> bool:
    """True si el usuario está autenticado."""
    return bool(
        request.user and request.user.is_authenticated
    )


def expand_project(request: Request) -> bool:
    """True si se solicita expansión de datos de proyecto."""
    return request.query_params.get(
        "expand_project", ""
    ).lower() in ("1", "true")


def expand_project_auth(request: Request) -> bool:
    """True si se solicita expansión Y el usuario está autenticado.

    Combina ``expand_project`` e ``is_authenticated`` para campos
    sensibles del proyecto (e.g. status_location).
    """
    return (
        expand_project(request)
        and is_authenticated(request)
    )