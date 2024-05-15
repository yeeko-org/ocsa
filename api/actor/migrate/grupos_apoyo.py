
from typing import Dict
from actor.migrate.common import ActorBase
from ocsa_legacy.models import GruposApoyo


class GruposApoyoToActorMigration(ActorBase):
    errors = []

    def __init__(self):
        super().__init__()

        grupos_apoyo = GruposApoyo.objects.all()

        for grupo_apoyo in grupos_apoyo:
            try:
                self.migrate_to_actor(grupo_apoyo)
            except Exception as e:
                raise e
                self.errors.append([grupo_apoyo, e])

    def migrate_to_actor(self, grupo_apoyo: GruposApoyo):
        if not grupo_apoyo.nombre:
            return

        grupo_name = grupo_apoyo.nombre

        grupo_apoyo_actor, created_actor = self.get_actor(grupo_name)

        mention = self.get_mention(grupo_apoyo)

        participation_list = []
        if grupo_apoyo.tipo_grupo_apoyo == "Empresa":
            participation_list.append("Partidario")

        if grupo_apoyo.tipo_grupo_apoyo in ["Opositor", "Opositores"]:
            participation_list.append("Acompañante solidario")

        self.add_participant(
            grupo_apoyo_actor, mention, participation_list,
            grupo_apoyo.interes)

        self.register_origin(
            grupo_apoyo_actor, grupo_apoyo.pk, "GruposApoyo", created_actor)
