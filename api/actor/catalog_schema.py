from ps_schema.registry import (
    catalog_registry,
    collection_registry, CollectionSchema, FilterRef,
    FilterGroupSchema,
)
from actor.models import Actor, Participant, Interest


@catalog_registry.register_filter_group
class ParticipantsFilterGroup(FilterGroupSchema):
    key_name = "participants"
    name = "Participante en Proyecto"
    plural_name = "Participantes en Proyectos"
    main_collection = "actor-actor"
    category_subtype = Participant


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

from api.export_blocks.actor import ActorExport  # noqa: E402
from api.export_blocks.participant import ParticipantExport  # noqa: E402
from api.views.actor import ActorViewSet, ActorMiniListViewSet  # noqa: E402
from api.views.note.mention_views import (  # noqa: E402
    ParticipantViewSet, InterestViewSet)


@collection_registry.register
class ActorSchema(CollectionSchema):
    model = Actor
    level = "primary"
    viewset_class = ActorViewSet
    mini_viewset_class = ActorMiniListViewSet
    icon = "recent_actors"
    color = "blue"
    xls_export_class = ActorExport
    sort_fields = [
        'status_location__order', 'name',
        {'mentions_count': 'Cantidad de menciones'},
    ]
    can_merge = True
    can_massive_edit = True
    all_filters = [
        FilterRef("participant_types"),
        FilterRef("belongs", hidden=True),
        FilterRef("indigenous_groups", hidden=True),
        FilterRef("sectors"),
        FilterRef("countries", hidden=True),
    ]


@collection_registry.register
class ParticipantSchema(CollectionSchema):
    model = Participant
    level = "relational"
    xls_export_class = ParticipantExport
    viewset_class = ParticipantViewSet


@collection_registry.register
class InterestSchema(CollectionSchema):
    model = Interest
    level = "secondary"
    viewset_class = InterestViewSet
    color = "cyan"
    can_massive_edit = True
