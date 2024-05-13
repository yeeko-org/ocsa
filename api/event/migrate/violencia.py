from typing import List, Optional
from actor.migrate.common import ActorBase
from actor.models import Participant, Sector, SectorGroup
from event.models import (
    Event, EventGroup, EventRole, EventSubtype, EventType, Involved)
from ocsa_legacy.models import (
    FormaHechoViolencia, HechosViolencia, SectorSocial, Violencia)
from source.models import Mention
from work_flux.models import StatusControl

from .generic_responsable_estatal import generic_responsable_estatal_desc
from .generic_responsable_no_estatal import generic_responsable_no_estatal_desc


class MigrateViolenciaToEvent(ActorBase):
    violencia: Violencia
    mention: Mention
    event: Event
    default_sector_group: SectorGroup
    sector_res_estatal: Sector
    sector_res_no_estatal: Sector
    need_review: StatusControl
    number_women: Optional[int] = None
    number_men: Optional[int] = None
    number_mix: Optional[int] = None

    sector_social_participant: Optional[Participant] = None  # Victima
    responsables_estatales: List[Participant] = []
    responsables_no_estatales: List[Participant] = []

    def __init__(self, violencia: Violencia):
        self.violencia = violencia
        self.mention = self.get_mention(self.violencia)
        self.event = self.get_event()
        self.set_involved_nums()
        self.default_sector_group, _ = SectorGroup.objects.get_or_create(
            name="Varios", is_collective=True)
        self.sector_res_estatal = self.get_or_create_sector(
            "Responsable Estatal")
        self.sector_res_no_estatal = self.get_or_create_sector(
            "Responsable No Estatal")

        self.need_review, _ = StatusControl.objects.get_or_create(
            name="need_review", group="validation",
            public_name="Requiere revisión")

        self.yeeko_comment = (
            "YEEKO: Se creó este nombre porque se identificó como nombre "
            "genérico, sin embargo, debe mejorar su nombre."
        )

        self.set_sector_social_actor()
        self.set_responsables_estatales()
        self.set_responsables_no_estatales()

    def get_or_create_sector(self, name: str) -> Sector:
        try:
            return Sector.objects.get(name=name)
        except Sector.DoesNotExist:
            return Sector.objects.create(
                name=name, sector_group=self.default_sector_group)

    def get_event(self) -> Event:
        hecho_nombre = getattr(self.violencia.hecho_violencia, "nombre", None)
        forma_nombre = getattr(
            self.violencia.forma_hecho_violencia, "nombre", None)

        fecha = getattr(self.violencia.temporalidad, "fecha", None)
        intervalo = getattr(self.violencia.temporalidad, "intervalo", None)

        if not (hecho_nombre and forma_nombre):
            raise Exception("Hecho o forma de violencia no encontrados")

        event_type = EventType.objects.get(name=hecho_nombre)
        if forma_nombre == "NE":
            event_subtype = None
            EventSubtype.objects.get_or_create(
                name=f"No Especificado de {hecho_nombre}")
        else:
            event_subtype = EventSubtype.objects.get(name=forma_nombre)

        event, _ = Event.objects.get_or_create(
            mention=self.mention,
            event_type=event_type,
            event_subtype=event_subtype
        )

        event.date = fecha if not event.date else event.date
        event.duration = intervalo if not event.duration else event.duration
        event.save()
        return event

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

        project_name = self.mention.project.official_name
        sector_s_name = (
            f"Víctima del sector {sector_s_name} del proyecto {project_name}")
        sector_social_actor, _ = self.get_actor(sector_s_name)

        similar_count = Sector.objects.filter(
            name__istartswith=sector_s_name).count()

        sector_social_victima = Sector.objects.create(
            name=sector_s_name +
            f" ({similar_count})" if similar_count else "",
            sector_group=self.default_sector_group
        )
        sector_social_actor.sector = sector_social_victima
        sector_social_actor.save()

        self.sector_social_participant = self.add_participant(
            sector_social_actor, self.mention, ["Víctima"],
            get_object=True)

    def get_not_generic_name(self, name: str) -> str:
        return f"{name} del proyecto {self.mention.project.official_name}"

    def set_responsables_estatales(self):
        responsables = self.violencia.responsable_estatal_desc
        if not responsables:
            return

        responsables = [
            r.strip() for r in responsables.split(";") if r.strip()]

        for responsable in responsables:
            need_review = False
            if responsable in generic_responsable_estatal_desc:
                responsable = self.get_not_generic_name(responsable)
                need_review = True
            self.responsable_estatal(responsable, need_review)

    def responsable_estatal(self, name: str, need_review: bool):
        actor, _ = self.get_actor(name)
        participant = self.add_participant(
            actor, self.mention, ["Por definir (de violencias)"],
            get_object=True)

        if not actor.sector:
            actor.sector = self.sector_res_estatal
        if need_review:
            actor.status_validation = self.need_review
            actor.comments = self.yeeko_comment

        actor.save()
        if participant:
            self.responsables_estatales.append(participant)

    def set_responsables_no_estatales(self):
        responsables = self.violencia.responsable_no_estatal_desc
        if not responsables:
            return

        responsables = [
            r.strip() for r in responsables.split(";") if r.strip()]

        for responsable in responsables:
            need_review = False
            if responsable in generic_responsable_no_estatal_desc:
                responsable = self.get_not_generic_name(responsable)
                need_review = True
            self.responsable_no_estatal(responsable, need_review)

    def responsable_no_estatal(self, name: str, need_review: bool):
        actor, _ = self.get_actor(name)
        participant = self.add_participant(
            actor, self.mention, ["Por definir (de violencias)"],
            get_object=True)

        if not actor.sector:
            actor.sector = self.sector_res_no_estatal
        if need_review:
            actor.status_validation = self.need_review
            actor.comments = self.yeeko_comment

        actor.save()
        if participant:
            self.responsables_estatales.append(participant)

    def set_involved(self, participant, role_name: str):
        event_role, _ = EventRole.objects.get_or_create(name=role_name)
        Involved.objects.create(
            event=self.event, participant=participant, event_role=event_role,
            number_women=self.number_women,
            number_men=self.number_men,
            number_mix=self.number_mix
        )

    def migrate(self):

        if self.sector_social_participant:
            self.set_involved(self.sector_social_participant, "Víctima")
        for responsable in self.responsables_estatales:
            self.set_involved(responsable, "Responsable")
        for responsable in self.responsables_no_estatales:
            self.set_involved(responsable, "Responsable")


class ViolenciaToEventMigrate:
    errors = []

    def __init__(self):
        self.hecho_violencia()
        self.forma_hecho_violencia()
        self.sector_social()
        for violencia in Violencia.objects.all():
            try:
                migrate_violencia = MigrateViolenciaToEvent(violencia)
                migrate_violencia.migrate()
            except Exception as e:
                self.errors.append([violencia, e])

    def hecho_violencia(self):
        default_group, _ = EventGroup.objects.get_or_create(
            name="Violencia", model_origin="HechosViolencia")
        for h_violencia in HechosViolencia.objects.all():
            if EventType.objects.filter(name=h_violencia.nombre).exists():
                continue
            EventType.objects.create(
                name=h_violencia.nombre,
                description=h_violencia.descripcion,
                group=default_group
            )

    def forma_hecho_violencia(self):
        for forma in FormaHechoViolencia.objects.exclude(nombre="NE"):
            EventSubtype.objects.create(
                name=forma.nombre,
                description=forma.descripcion
            )

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
