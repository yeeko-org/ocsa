"""Construcción de los índices precalculados que alimentan el filtrado
del mapa en el frontend (rediseño, sesión 4).

Dos índices, ambos *directos* (keyed por la entidad, no invertidos: el
índice invertido lo arma el cliente en una pasada al montar):

- ``build_facet_index`` → ``{project_id: {e, i, s, p}}`` con las cuatro
  dimensiones que cuelgan de ``Mention`` y que el cliente no puede
  derivar del geojson (tipos de evento, de afectación, subtipos y tipos
  de participación). Megaproyecto, extractivismo y estado NO viajan aquí:
  el front los deriva de la data que ya tiene.
- ``build_actor_index`` → catálogo completo de actores + el mapeo
  ``actor → [project_ids]`` para resolver el filtro de actor en cliente.

Lógica pura de ORM, sin DRF: reutilizable por las vistas y por el
management command del cron.
"""

from collections import defaultdict

from actor.models import Actor, Participant
from source.models import Mention

# Solo proyectos públicos entran al índice (mismo criterio que el
# endpoint de ubicaciones del mapa).
PUBLIC_FILTER = {"project__status_validation__is_public": True}

# Llave compacta del payload → ruta del id de faceta desde Mention.
FACET_DIMENSIONS = {
    "e": "events__event_type_id",
    "i": "impacts__impact_type_id",
    "s": "impacts__impact_subtype_id",
    "p": "participants__participant_types",
}


def build_facet_index() -> dict:
    """Devuelve ``{str(project_id): {dim: [ids ordenados]}}``.

    Una consulta por dimensión (join simple + ``distinct``); las
    dimensiones vacías de un proyecto se omiten para ahorrar bytes (el
    cliente trata la clave ausente como lista vacía).
    """
    index: dict = defaultdict(lambda: defaultdict(set))
    public_mentions = Mention.objects.filter(**PUBLIC_FILTER)

    for key, facet_path in FACET_DIMENSIONS.items():
        pairs = public_mentions.values_list(
            "project_id", facet_path).distinct()
        for project_id, facet_id in pairs:
            if facet_id is not None:  # menciones sin esa faceta
                index[project_id][key].add(facet_id)

    return {
        str(project_id): {
            key: sorted(ids) for key, ids in dimensions.items()
        }
        for project_id, dimensions in index.items()
    }


def build_actor_index() -> dict:
    """Catálogo de actores + mapeo ``actor → proyectos públicos``.

    ``actors`` incluye los campos directos del modelo ``Actor`` que el
    buscador principal (MiniSearch) necesitará pre-cargados; las
    posiciones (por-participación) se dejan para la sesión 4.1.
    """
    # belongs es M2M: lo agrego primero en un dict para no consultarlo
    # por actor (evita N+1).
    belongs_by_actor: dict = defaultdict(list)
    belongs_pairs = Actor.objects.filter(
        belongs__isnull=False).values_list("id", "belongs")
    for actor_id, belong_id in belongs_pairs:
        belongs_by_actor[actor_id].append(belong_id)

    actors = [
        {
            "id": actor_id,
            "name": name,
            "sector": sector_id,
            "belongs": sorted(belongs_by_actor.get(actor_id, [])),
        }
        for actor_id, name, sector_id in Actor.objects.values_list(
            "id", "name", "sector_id")
    ]

    actor_projects: dict = defaultdict(set)
    participant_pairs = Participant.objects.filter(
        mention__project__status_validation__is_public=True
    ).values_list("actor_id", "mention__project_id").distinct()
    for actor_id, project_id in participant_pairs:
        actor_projects[actor_id].add(project_id)

    return {
        "actors": actors,
        "actor_projects": {
            str(actor_id): sorted(project_ids)
            for actor_id, project_ids in actor_projects.items()
        },
    }
