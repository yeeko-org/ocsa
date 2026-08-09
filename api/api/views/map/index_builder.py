"""Construcción de los índices precalculados que alimentan el filtrado
del mapa en el frontend (rediseño, sesión 4).

Dos índices, ambos *directos* (keyed por la entidad, no invertidos: el
índice invertido lo arma el cliente en una pasada al montar):

- ``build_facet_index`` → ``{project_id: {e, i, s, p}}`` con las cuatro
  dimensiones que cuelgan de ``Mention`` y que el cliente no puede
  derivar del geojson (tipos de evento, de afectación, subtipos y tipos
  de participación). Megaproyecto, extractivismo y estado NO viajan aquí:
  el front los deriva de la data que ya tiene.
- ``build_actor_index`` → catálogo de actores con al menos un proyecto
  público + el mapeo ``actor → {project_id: [position_ids]}`` para
  resolver en cliente el filtro de actor y el de posición.

Lógica pura de ORM, sin DRF: reutilizable por las vistas y por el
management command del cron.
"""

from collections import defaultdict

from actor.models import Actor, Participant
from classify.models import ParticipantGroup
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
    """Catálogo de actores + mapeo ``actor → proyecto → posiciones``.

    ``actors`` incluye los campos directos del modelo ``Actor`` que el
    buscador principal (MiniSearch) necesitará pre-cargados.

    El catálogo se restringe a los actores que aparecen en
    ``actor_projects``: un actor sin proyecto público daría cero
    resultados al seleccionarlo, y publicarlo en un endpoint AllowAny
    expondría además actores no validados o incompletos.

    La posición se guarda por par (actor, proyecto) y no por actor: un
    mismo actor puede oponerse a un proyecto y apoyar otro, e incluso
    acumular varias posiciones dentro del mismo proyecto (de ahí que sea
    una lista). La fuente canónica es ``ParticipantGroup``, no el campo
    ``ParticipantType.position``. Una lista vacía significa participación
    sin tipo asignado (o con tipo sin grupo): el par queda fuera del
    filtro de posición pero sigue en el mapa, porque el proyecto es real.
    """
    # Un par (actor, proyecto) rinde una fila por grupo de participación;
    # None cuando la participación no tiene tipo o el tipo no tiene grupo.
    actor_projects: dict = defaultdict(lambda: defaultdict(set))
    participant_rows = Participant.objects.filter(
        mention__project__status_validation__is_public=True
    ).values_list(
        "actor_id", "mention__project_id",
        "participant_types__participant_group_id").distinct()
    for actor_id, project_id, group_id in participant_rows:
        positions = actor_projects[actor_id][project_id]
        if group_id is not None:
            positions.add(group_id)

    public_actor_ids = list(actor_projects)

    # belongs es M2M: lo agrego primero en un dict para no consultarlo
    # por actor (evita N+1).
    belongs_by_actor: dict = defaultdict(list)
    belongs_pairs = Actor.objects.filter(
        id__in=public_actor_ids, belongs__isnull=False
    ).values_list("id", "belongs")
    for actor_id, belong_id in belongs_pairs:
        belongs_by_actor[actor_id].append(belong_id)

    actors = [
        {
            "id": actor_id,
            "name": name,
            "sector": sector_id,
            "belongs": sorted(belongs_by_actor.get(actor_id, [])),
        }
        for actor_id, name, sector_id in Actor.objects.filter(
            id__in=public_actor_ids
        ).values_list("id", "name", "sector_id")
    ]

    positions = [
        {"id": group_id, "name": name}
        for group_id, name in ParticipantGroup.objects.values_list(
            "id", "name")
    ]

    return {
        "actors": actors,
        "positions": positions,
        "actor_projects": {
            str(actor_id): {
                str(project_id): sorted(position_ids)
                for project_id, position_ids in sorted(projects.items())
            }
            for actor_id, projects in actor_projects.items()
        },
    }
