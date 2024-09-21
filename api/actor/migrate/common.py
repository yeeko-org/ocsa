from typing import Dict, Optional, Tuple
from source.models import Mention, Note
from project.models import Project
from actor.models import (
    Actor, Interest, OriginReference, Participant)
from classify.models import ParticipantType, Belong, SectorGroup, Sector


class ActorBase:
    mentions = {}
    actors: Dict[str, Actor] = {}
    errors = []

    def get_actor(
            self, name: Optional[str], std_name: Optional[str] = None
    ) -> Tuple[Actor, bool]:
        is_created = False

        if not name and not std_name:
            raise ValueError("Name or std_name must be provided")
        if not std_name:
            std_name = text_normalizer(name)

        final_actor = self.actors.get(std_name)
        if final_actor:
            # No es necesario, el diccionario y las instancias son apuntadores
            # self.actors[std_name] = final_actor
            final_actor.append_alternative_name(name)
            return final_actor, is_created

        try:
            # Existe fuera de la migracion actual con std_name
            actor = Actor.objects.get(std_name=std_name)
        except Actor.DoesNotExist:
            try:
                # Existe con name pero no con std_name
                actor = Actor.objects.get(name=name)
                if not actor.std_name:
                    # Ricardo, se remplaza si existe?
                    actor.std_name = std_name
                    actor.save()

            except Actor.DoesNotExist:
                actor = Actor.objects.create(name=name, std_name=std_name)
                is_created = True

        actor.append_alternative_name(name)
        self.actors[std_name] = actor
        return actor, is_created

    def add_parent(self, actor: Actor, parent: Actor):
        if not parent:
            return
        if actor.parent_actor:
            self.errors.append(
                [actor,
                 f"Actor {actor.pk} already has a parent {actor.parent_actor.pk}"]
            )
            return
        actor.parent_actor = parent  # type: ignore

    def add_participant(
        self, actor: Actor, mention: Optional[Mention],
        participant_types: Optional[list] = None,
        interest: Optional[str] = None,
        get_object: Optional[bool] = False
    ):
        if not mention:
            return
        participant, _ = Participant.objects.get_or_create(
            actor=actor, mention=mention)

        if participant_types:
            for participant_type in participant_types:
                pt, _ = ParticipantType.objects.get_or_create(
                    name=participant_type)
                participant.participant_types.add(pt)
        if interest:
            self.set_interest(participant, interest)

        if get_object:
            return participant

    def get_participant(
        self, actor: Actor, mention: Mention,
        participant_types: Optional[list] = None,
        interest: Optional[str] = None
    ) -> Participant:
        participant = self.add_participant(
            actor, mention, participant_types, interest, get_object=True
        )

        if not participant:
            raise ValueError(f"Error with actor {actor} and mention {mention}")

        return participant

    def get_mention(self, instance) -> Mention:
        nota_id: Optional[int] = getattr(instance, "nota_id", None)
        proyecto_id: Optional[int] = getattr(instance, "proyecto_id", None)

        if not (nota_id and proyecto_id):
            error = (
                f"Error with instance {instance.__class__.__name__}"
                f" {instance.pk}: {instance}"
                f" (nota_id: {nota_id}, proyecto_id: {proyecto_id})"
            )
            raise ValueError(error)

        key_name = f"{nota_id}-{proyecto_id}"
        if key_name in self.mentions:
            return self.mentions[key_name]

        project = Project.objects.filter(
            proyecto_id_ref=proyecto_id).first()
        note = Note.objects.filter(nota_id_ref=nota_id).first()

        if not (note and project):
            error = (f"Not proyecto {proyecto_id} or note"
                     f" {nota_id} found")

            self.errors.append([instance, error])

        mention, _ = Mention.objects.get_or_create(
            note=note,
            project=project)

        self.mentions[key_name] = mention

        return mention

    def get_sector_group_default(self) -> SectorGroup:
        if not hasattr(self, "_default_sector_group"):
            self._default_sector_group, _ = SectorGroup.objects.get_or_create(
                name="Varios", is_collective=True)
        return self._default_sector_group

    def set_sector(self, actor: Actor, sector: str):
        if not sector:
            return

        sector_obj, _ = Sector.objects.get_or_create(
            name=sector, defaults={
                "sector_group": self.get_sector_group_default()}
        )

        if not actor.sector:
            actor.sector = sector_obj
        elif actor.sector != sector_obj:
            actor_validation = actor.sector.status_validation_id  # type: ignore
            sector_validation = sector_obj.status_validation_id  # type: ignore
            if actor.sector.name == "Contradictorio":
                error = (f"YEEKO: hay sectores contradictorios:"
                         f" {actor.sector.name} y {sector_obj.name}")
                actor.add_comment(error)
                self.errors.append([actor, error])
            elif actor_validation and "reclassify" in actor_validation:
                actor.sector = sector_obj
            elif sector_validation and "reclassify" in sector_validation:
                pass
            else:
                sector_contradictory = Sector.objects.get(
                    name="Contradictorio")
                error = (f"YEEKO: hay sectores contradictorios:"
                         f" {actor.sector.name} y {sector_obj.name}")
                self.errors.append([actor, error])
                actor.add_comment(error)
                actor.sector = sector_contradictory
        actor.save()

    def set_interest(self, participant: Participant, interest: str):
        if not interest:
            return
        Interest.objects.create(
            participant=participant,
            text=interest,
        )

    def register_origin(
            self, actor: Actor, origin_id: str, type_model: str,
            actor_created: bool, field: Optional[str] = None, **kwargs
    ) -> None:
        OriginReference.objects.create(
            actor=actor,
            origin_id=origin_id,
            type_model=type_model,
            field_name=field,
            actor_created=actor_created,
            data=kwargs
        )

    def get_belong(self, key: str) -> Belong:
        try:
            return Belong.objects.get(key_name=key)
        except Belong.DoesNotExist:
            return Belong.objects.create(key_name=key, name=key)


def text_normalizer(text, to_headers=False) -> str:
    import re
    import unidecode
    if not text:
        return text
    final_text = text.upper().strip()
    final_text = unidecode.unidecode(final_text)
    final_text = final_text.replace('Ü', 'U')
    final_text = re.sub(r'[^a-zA-Z0-9\s]', '', final_text)
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(
        r'(^A-Z)(SA DE CV|SAPI DE CV|SA DE RL|SAB DE CV|S DE RL|S DE RL DE CV)', '', final_text)
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(r'[^A-Z0-9]', '', final_text)
    final_text = final_text.strip()
    return final_text
