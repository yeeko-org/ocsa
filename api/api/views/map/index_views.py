"""Endpoints de los índices precalculados del mapa (rediseño, sesión 4).

- ``ProjectFacetsView``  → GET público, facetas por proyecto.
- ``MapActorsView``      → GET público, catálogo de actores + mapeo.
- ``RebuildMapIndexView``→ POST admin, fuerza la reconstrucción.

Las vistas son delgadas a propósito: construir, cachear y resolver
frescura vive en ``index_cache``; la lógica de datos en ``index_builder``.
"""

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .index_cache import (
    ACTOR_CACHE_KEY, FACET_CACHE_KEY, build_actors_payload,
    build_facets_payload, cached_index, rebuild_all)


class ProjectFacetsView(APIView):
    """Índice directo ``{project_id: {e, i, s, p}}`` para filtrar en el
    cliente. Solo proyectos públicos."""
    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        return Response(
            cached_index(FACET_CACHE_KEY, build_facets_payload))


class MapActorsView(APIView):
    """Catálogo de actores + ``actor_projects`` para el buscador y el
    filtro de actor en el cliente."""
    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        return Response(
            cached_index(ACTOR_CACHE_KEY, build_actors_payload))


class RebuildMapIndexView(APIView):
    """Fuerza la reconstrucción de ambos índices (acción de operación).
    El cron diario hace lo mismo vía el management command."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request) -> Response:
        summary = rebuild_all()
        return Response({"detail": "Índices reconstruidos.", **summary})
