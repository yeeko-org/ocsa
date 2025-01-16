from typing import List, Optional

from event.migrate.event_base import EventBase
from actor.models import Participant
from classify.models import SectorGroup, Sector
from event.models import (
    Event, EventGroup, InvolvedRole, EventSubtype, EventType, Involved)
from ocsa_legacy.models import (
    FormaHechoViolencia, HechosViolencia, SectorSocial, Violencia)

from .generics import generic_responsables


class MigrateViolenciaToEvent(EventBase):
    violencia: Violencia
    sector_res_estatal: Sector
    sector_res_no_estatal: Sector
    number_women: Optional[int] = None
    number_men: Optional[int] = None
    number_mix: Optional[int] = None

    victima_participante: Optional[Participant] = None  # Victima
    responsables: dict[str, List[Participant]]
    resp_types = ["estatal", "no_estatal"]

    def __init__(self, violencia: Violencia):
        self.violencia = violencia
        self.mention = self.get_mention(self.violencia)
        self.event = self.get_main_event()
        viol_to_ubic_query = self.violencia.violenciatoubicacion_set.all()
        self.set_locations(viol_to_ubic_query)
        self.set_involved_nums()
        self.sector_res = {
            "estatal": self.get_or_create_sector("Institución del Estado"),
            "no_estatal": self.get_or_create_sector("Responsable No Estatal")
        }

        self.yeeko_comment = (
            "YEEKO: Se creó este nombre porque se identificó como nombre "
            "genérico, sin embargo, debe mejorar su nombre."
        )

        self.responsables = {}
        self.reset_responsables()
        self.set_sector_social_actor()
        for resp_type in self.resp_types:
            self.set_responsables(resp_type)

    def reset_responsables(self):
        for resp_type in self.resp_types:
            self.responsables[resp_type] = []

    def get_or_create_sector(self, name: str) -> Sector:
        sector, _ = Sector.objects.get_or_create(
            name=name, defaults={"sector_group": self.default_sector_group})
        return sector

    def get_main_event(self) -> Event:
        hecho_nombre = getattr(self.violencia.hecho_violencia, "nombre", None)
        forma_nombre = getattr(
            self.violencia.forma_hecho_violencia, "nombre", None)

        return self.get_event(self.violencia, hecho_nombre, forma_nombre)

    def set_involved_nums(self):
        num_victimas = self.violencia.num_victimas
        if not num_victimas:
            return
        if not num_victimas.isdigit():
            return
        num_victimas = int(num_victimas)
        is_mujeres = self.violencia.is_mujeres
        is_hombres = self.violencia.is_hombres

        if not (is_mujeres and is_hombres):
            self.number_mix = num_victimas

        elif is_mujeres and is_hombres:
            if num_victimas == 2:
                self.number_women = 1
                self.number_men = 1
            else:
                self.number_mix = num_victimas
        else:
            if is_mujeres:
                self.number_women = num_victimas
            if is_hombres:
                self.number_men = num_victimas

    def set_sector_social_actor(self):
        sector_s_name = getattr(
            self.violencia.sector_social_victima, "nombre", None)
        if not sector_s_name:
            return

        project_name = self.mention.project.name
        # sector_s_name = (
        #     f"Víctima del sector {sector_s_name} del proyecto {project_name}")
        actor_name = (
            f"Víctima del sector {sector_s_name} del proyecto {project_name}")
        actor_victima, _ = self.get_actor(actor_name)

        similar_count = Sector.objects\
            .filter(name__istartswith=sector_s_name).count()

        # sector_social_victima = Sector.objects.create(
        #     name=sector_s_name +
        #     f" ({similar_count})" if similar_count else "",
        #     sector_group=self.default_sector_group
        # )
        sector_social_victima, created = Sector.objects.get_or_create(
            name=sector_s_name,
            sector_group=self.default_sector_group
        )
        actor_victima.sector = sector_social_victima
        actor_victima.status_validation_id = "need_reclassify"
        actor_victima.save()
        actor_victima.add_comment(
            f"YEEKO: Se creó este nombre porque se identificó como nombre "
            "genérico, sin embargo, debe mejorar su nombre."
        )

        # sector_social_actor.belongs.add(self.get_belong("is_leader"))

        self.victima_participante = self.add_participant(
            actor_victima, self.mention, get_object=True)

    def get_not_generic_name(self, name: str) -> str:
        return f"{name} del proyecto {self.mention.project.name}"

    def set_responsables(self, resp_type: str):
        field = f"responsable_{resp_type}_desc"
        responsables = getattr(self.violencia, field)
        if not responsables:
            return

        responsables = [
            r.strip() for r in responsables.split(";") if r.strip()]

        for responsable in responsables:
            need_review = False
            if responsable in generic_responsables[resp_type]:
                responsable = self.get_not_generic_name(responsable)
                need_review = True
            self.add_responsable(responsable, need_review, resp_type)

    def add_responsable(self, name: str, need_review: bool, resp_type: str):

        actor, _ = self.get_actor(name)
        participant = self.add_participant(
            actor, self.mention, ["Por definir (de violencias)"],
            get_object=True)

        if not actor.sector:
            actor.sector = self.sector_res[resp_type]
        if need_review:
            actor.status_validation_id = "need_review"
            actor.comments = self.yeeko_comment

        actor.save()
        if participant:
            self.responsables[resp_type].append(participant)

    def set_involved(self, participant, role_name: str):
        involved_role, _ = InvolvedRole.objects.get_or_create(name=role_name)
        Involved.objects.create(
            event=self.event,
            participant=participant,
            involved_role=involved_role,
            number_women=self.number_women,
            number_men=self.number_men,
            number_mix=self.number_mix
        )

    def migrate(self):

        if self.victima_participante:
            self.set_involved(self.victima_participante, "Víctima")
        for resp_type in self.resp_types:
            for responsable in self.responsables[resp_type]:
                self.set_involved(responsable, "Responsable")


class ViolenciaToEventMigrate:
    errors = []

    def __init__(self):
        import traceback
        self.hecho_violencia()
        self.forma_hecho_violencia()
        self.sector_social()
        for violencia in Violencia.objects.all():
            try:
                migrate_violencia = MigrateViolenciaToEvent(violencia)
                migrate_violencia.migrate()
            except Exception as e:
                error_ = traceback.format_exc()
                self.errors.append([violencia, e])
                print(error_)

    def hecho_violencia(self):
        default_group, created = EventGroup.objects.get_or_create(
            name="Violencia", model_origin="HechosViolencia")
        if created:
            default_group.icon = 'voice_over_off'
            default_group.color = 'deep-orange'
            default_group.save()

        for h_violencia in HechosViolencia.objects.all():
            if EventType.objects.filter(name=h_violencia.nombre).exists():
                continue
            EventType.objects.create(
                name=h_violencia.nombre,
                description=h_violencia.descripcion,
                event_group=default_group
            )

    def forma_hecho_violencia(self):
        for forma in FormaHechoViolencia.objects.exclude(nombre="NE"):
            event_subtype, is_created = EventSubtype.objects.get_or_create(
                name=forma.nombre
            )
            if is_created:
                event_subtype.description = forma.descripcion
                event_subtype.save()

    def sector_social(self):
        collective_group, _ = SectorGroup.objects.get_or_create(
            name="Varios", is_collective=True)
        individual_group, _ = SectorGroup.objects.get_or_create(
            name="Individuos (Varios)", is_collective=False)
        special_sectors = [
            "Trabajador de la empresa", "Otro (Abogado opositor)",
            "Periodista", "Abogado", "Activista", "Agente Federal",
            "Activista", "Defensor Ambiental", "Comerciante",
            "Defensor Ambiental", "Profesor", "Comunero",
            "Defensor del territorio", "Comunicador", "Profesora", "Alcalde"
        ]
        for sector_social in SectorSocial.objects.all():
            if not sector_social.nombre:
                continue
            group = individual_group if sector_social.nombre in special_sectors \
                else collective_group

            if Sector.objects\
                    .filter(name=sector_social.nombre, sector_group=group)\
                    .exists():
                continue

            Sector.objects.create(
                name=sector_social.nombre,
                sector_group=group,
                status_validation_id="need_reclassify"
            )
