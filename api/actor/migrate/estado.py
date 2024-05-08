from typing import Optional
from ocsa_legacy.models import Estado
from source.models import Mention
from work_flux.models import StatusControl
from actor.migrate.common import ActorBase


class EstadoToActorMigration(ActorBase):
    errors = []

    def __init__(self):
        super().__init__()
        estados = Estado.objects.all()

        self.need_review, _ = StatusControl.objects.get_or_create(
            name="need_review", group="validation",
            public_name="Requiere revisión")

        for estado in estados:
            try:
                self.migrate_to_actor(estado)
            except Exception as e:
                raise e
                self.errors.append([estado, e])

    def migrate_to_actor(self, estado: Estado):

        mention = self.get_mention(estado)
        self.add_status_project(mention)

        self.migrate_to_actor_from_name(
            mention, estado, "instituciones_a_favor_proyecto", ["Estado"])

        self.migrate_to_actor_from_name(
            mention, estado, "instituciones_mediadoras", ["Mediador"])

        self.migrate_to_actor_from_name(
            mention, estado, "instituciones_atienden_reclamos",
            ["Atención a reclamos"])

    def migrate_to_actor_from_name(
            self, mention: Mention,
            estado: Estado,
            attr_institution_name: str,
            participant_types: Optional[list] = None
    ):
        institution_name = getattr(estado, attr_institution_name)
        if not institution_name:
            return
        institution_actor, created_actor = self.get_actor(institution_name)

        self.add_participant(
            institution_actor, mention, participant_types)

        self.register_origin(
            institution_actor, estado.pk, "Estado", created_actor,
            by=attr_institution_name, mention_id=mention.pk
        )
