from typing import Optional
from source.models import Mention, Note
from project.models import Project
from actor.models import Actor, Participant, ParticipantType
from ocsa_legacy.models import Proyecto, Nota


class ActorBase:
    mentions = {}
    actors = {}

    def __init__(self):
        self.errors = []

    def get_actor(self, name: str, std_name: Optional[str] = None):
        if not name and not std_name:
            raise ValueError("Name or std_name must be provided")
        if not std_name:
            std_name = text_normalizer(name)
        if std_name in self.actors:
            final_actor = self.actors[std_name]
            if final_actor.name != name:
                if name not in final_actor.alternative_names:
                    final_actor.alternative_names.append(name)
                    final_actor.save()
                    self.actors[std_name] = final_actor
            return self.actors[std_name]
        try:
            actor = Actor.objects.get(std_name=std_name)
        except Actor.DoesNotExist:
            actor = Actor.objects.create(name=name, std_name=std_name)
        self.actors[std_name] = actor

    def add_parent(self, actor: Actor, parent: Actor):
        if not parent:
            return
        if actor.parent_actor:
            self.errors.append(
                [actor,
                 f"Actor {actor.pk} already has a parent {actor.parent_actor.pk}"]
            )
            return
        actor.parent_actor = parent

    def add_participant(self, actor: Actor, mention: Mention,
                        participant_types: Optional[list] = None):
        participant, _ = Participant.objects.get_or_create(
            actor=actor, mention=mention)
        if participant_types:
            for participant_type in participant_types:
                pt, _ = ParticipantType.objects.get_or_create(
                    name=participant_type)
                participant.participant_types.add(pt)

    def get_mention(self, instance):

        if not (instance.nota and instance.proyecto):
            error = (f"Error with instance {instance.__class__.__name__}"
                     f" {instance.pk}: {instance}")
            print(error)
            self.errors.append([instance, error])
            return None

        key_name = f"{instance.nota_id}-{instance.proyecto_id}"
        if key_name in self.mentions:
            return self.mentions[key_name]

        project = Project.objects.filter(
            proyecto_id_ref=instance.proyecto_id).first()
        note = Note.objects.filter(nota_id_ref=instance.nota_id).first()

        if not (note and project):
            error = (f"Not proyecto {instance.proyecto.pk} or note"
                     f" {instance.nota.pk} found")
            print(error)
            self.errors.append([instance, error])

        mention, _ = Mention.objects.get_or_create(
            note=note,
            project=project)

        self.mentions[key_name] = mention

        return mention


def text_normalizer(text, to_headers=False):
    import re
    import unidecode
    if not text:
        return text
    final_text = text.upper().strip()
    final_text = unidecode.unidecode(final_text)
    final_text = final_text.replace('Ü', 'U')
    final_text = re.sub(r'[^a-zA-Z0-9\s]', '', final_text)
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(r'[^A-Z][SA DE CV|SAPI DE CV|SA DE RL|SAB DE CV|S DE RL|S DE RL DE CV]', '', final_text)
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(r'[^A-Z]', '', final_text)
    final_text = final_text.strip()
    return final_text

