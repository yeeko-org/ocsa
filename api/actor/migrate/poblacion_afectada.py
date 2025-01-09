
from typing import Dict
from actor.migrate.common import ActorBase
from classify.models import Belong, IndigenousGroup
from ocsa_legacy.models import CatSubpoblacionAfectada, PoblacionAfectada


class PoblacionAfectadaToActorMigration(ActorBase):
    errors = []
    indigenous_groups: Dict[str, IndigenousGroup] = {}

    def __init__(self):
        super().__init__()

        self.set_indigenous_group()

        poblacion_afectada = PoblacionAfectada.objects.all()

        for poblacion_afectada in poblacion_afectada:
            try:
                self.migrate_to_actor(poblacion_afectada)
            except Exception as e:
                self.errors.append([poblacion_afectada, e])

    def set_indigenous_group(self):
        for subpoblacion_afectada in CatSubpoblacionAfectada.objects.all():
            nombre = subpoblacion_afectada.nombre
            if not nombre:
                continue

            indigenous_group, _ = IndigenousGroup.objects.get_or_create(
                name=nombre, description=subpoblacion_afectada.descripcion,
                status_validation_id='original')
            self.indigenous_groups[nombre] = indigenous_group

    def get_indigenous_group(self, name: str) -> IndigenousGroup:
        indigenous_group = self.indigenous_groups.get(name)
        if not indigenous_group:
            indigenous_group, _ = IndigenousGroup.objects.get_or_create(
                name=name, status_validation_id='original')
            self.indigenous_groups[name] = indigenous_group
        return indigenous_group

    def migrate_to_actor(self, poblacion_afectada: PoblacionAfectada):
        if not poblacion_afectada.descripcion:
            return

        poblacion_name = poblacion_afectada.descripcion
        if poblacion_name == '""':
            poblacion_name = f'"Desconocida - {poblacion_afectada.pk}"'

        poblacion_afectada_actor, created_actor = self.get_actor(
            poblacion_name)

        subpoblacion_afectada_name = getattr(
            poblacion_afectada.subpoblacion_afectada, "nombre", None)
        if subpoblacion_afectada_name:
            indigenous_group = self.get_indigenous_group(
                subpoblacion_afectada_name)
            poblacion_afectada_actor.indigenous_group = indigenous_group

        poblacion_afectada_actor.is_incomplete = '"' in poblacion_name
        poblacion_afectada_actor.save()

        cat_poblacion_name = getattr(
            poblacion_afectada.poblacion_afectada, "nombre", None)
        if cat_poblacion_name:
            belong_data = {
                "is_indigena": ["Indígena"],
                "is_farmer": ["Campesino/Comunero/Ejidatario"],
                "is_worker": ["Trabajador de empresa"],
                "is_habitant": ["Pobladores", "Vecinos"],
            }
            for key, values in belong_data.items():
                if cat_poblacion_name in values:
                    poblacion_afectada_actor.belongs.add(self.get_belong(key))
                    break

        subpoblacion_id = str(getattr(
            poblacion_afectada.subpoblacion_afectada, "id", None))

        if subpoblacion_id.isdigit() and int(subpoblacion_id) > 4:
            poblacion_afectada_actor.belongs.add(
                self.get_belong("is_indigena"))

        poblacion_afectada_actor.belongs.add(self.get_belong("is_affected"))

        mention = self.get_mention(poblacion_afectada)

        self.add_participant(
            poblacion_afectada_actor, mention, ["PoblacionesAfectadas"],
            poblacion_afectada.interes)

        self.register_origin(
            poblacion_afectada_actor, poblacion_afectada.pk,
            "PoblacionAfectada", created_actor)
