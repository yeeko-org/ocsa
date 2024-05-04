from typing import Optional
from django.db.models import F
from source.models import Mention, Note, StatusHistory
from project.models import Project
from actor.models import Actor, Interest, Participant, ParticipantType
from ocsa_legacy.models import EstatusProyectos, Proyecto, Nota
from space_time.models import StatusProject


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
        actor.parent_actor = parent  # type: ignore

    def add_participant(
        self, actor: Actor, mention: Mention,
        participant_types: Optional[list] = None
    ):
        participant, _ = Participant.objects.get_or_create(
            actor=actor, mention=mention)

        if participant_types:
            for participant_type in participant_types:
                pt, _ = ParticipantType.objects.get_or_create(
                    name=participant_type)
                participant.participant_types.add(pt)

    def get_mention(self, instance):
        nota_id: Optional[int] = getattr(instance, "nota_id", None)
        proyecto_id: Optional[int] = getattr(instance, "proyecto_id", None)

        if not (nota_id and proyecto_id):
            error = (f"Error with instance {instance.__class__.__name__}"
                     f" {instance.pk}: {instance}")
            print(error)
            self.errors.append([instance, error])
            return None

        key_name = f"{nota_id}-{proyecto_id}"
        if key_name in self.mentions:
            return self.mentions[key_name]

        project = Project.objects.filter(
            proyecto_id_ref=proyecto_id).first()
        note = Note.objects.filter(nota_id_ref=nota_id).first()

        if not (note and project):
            error = (f"Not proyecto {proyecto_id} or note"
                     f" {nota_id} found")
            print(error)
            self.errors.append([instance, error])

        mention, _ = Mention.objects.get_or_create(
            note=note,
            project=project)

        self.mentions[key_name] = mention

        return mention

    def add_status_project(self, mention: Mention):
        query_estatus_proyectos = EstatusProyectos.objects\
            .filter(
                nota__id=mention.note.nota_id_ref,
                proyecto__id=mention.project.proyecto_id_ref)\
            .annotate(
                estatus_nombre=F('estatus__nombre'),
                tem_date=F('temporalidad__fecha'),
                tem_interval=F('temporalidad__interval'),
                cat_tem_nombre=F('temporalidad__cat_temporalidad__nombre'),
            )

        for estatus_proyecto in query_estatus_proyectos:
            estatus_nombre = estatus_proyecto.estatus_nombre  # type: ignore
            cat_tem_nombre = estatus_proyecto.cat_tem_nombre  # type: ignore
            tem_date = estatus_proyecto.tem_date  # type: ignore
            tem_interval = estatus_proyecto.tem_interval  # type: ignore

            any_data = any(
                [estatus_nombre, cat_tem_nombre, tem_date, tem_interval])

            if any_data:
                continue

            status_project = None
            if estatus_nombre:
                status_project = StatusProject.objects.get_or_create(
                    name=estatus_nombre)

            _, _ = StatusHistory.objects.get_or_create(
                mention=mention,
                status_project=status_project,
                date=tem_date,
                interval=tem_interval,
                type_temporalidad=cat_tem_nombre
            )


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
    final_text = re.sub(
        r'[^A-Z][SA DE CV|SAPI DE CV|SA DE RL|SAB DE CV|S DE RL|S DE RL DE CV]', '', final_text)
    final_text = re.sub(r' +', ' ', final_text)
    final_text = re.sub(r'[^A-Z]', '', final_text)
    final_text = final_text.strip()
    return final_text
