"""Política de caché de los índices del mapa.

Envuelve los builders puros (``index_builder``) con el timestamp
``built_at`` y la lógica de lectura/escritura en caché (Redis, TTL 24 h).
Vive aparte de las vistas para que el management command del cron lo
reutilice sin depender de DRF.
"""

from django.core.cache import cache
from django.utils import timezone

from .index_builder import build_actor_index, build_facet_index

FACET_CACHE_KEY = "map:facet_index"
ACTOR_CACHE_KEY = "map:actor_index"
INDEX_TTL = 60 * 60 * 24  # 24 horas


def _stamp(payload: dict) -> dict:
    """Antepone ``built_at`` al payload (momento de construcción)."""
    return {"built_at": timezone.now().isoformat(), **payload}


def build_facets_payload() -> dict:
    return _stamp({"facets": build_facet_index()})


def build_actors_payload() -> dict:
    return _stamp(build_actor_index())


def cached_index(cache_key: str, builder, force: bool = False) -> dict:
    """Lee el índice de caché; lo (re)construye si falta o si ``force``.

    Único punto donde se toca la caché — evita repetir el patrón
    leer-o-construir en cada vista y en el comando del cron.
    """
    if not force:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    payload = builder()
    cache.set(cache_key, payload, INDEX_TTL)
    return payload


def rebuild_all() -> dict:
    """Fuerza la reconstrucción de ambos índices. Usado por el endpoint
    admin y por el management command. Devuelve un resumen."""
    facets = cached_index(FACET_CACHE_KEY, build_facets_payload, force=True)
    actors = cached_index(ACTOR_CACHE_KEY, build_actors_payload, force=True)
    return {
        "facets_built_at": facets["built_at"],
        "actors_built_at": actors["built_at"],
        "projects": len(facets["facets"]),
        "actors": len(actors["actors"]),
    }
