from typing import Any, Dict, List, Optional
from actor.migrate.common import ActorBase
from actor.models import Participant
from classify.models import SectorGroup, Sector
from event.models import Event, EventGroup, EventLocation, EventRole, EventSubtype, EventType, Involved
from ocsa_legacy.models import AccionColectivaToUbicacion, FormaAC, Opositores, OpositoresToAC, SectorSocial, AccionesColectivas, SubformaAC
from source.models import Mention
from space_time.models import Location
from work_flux.models import StatusControl


class MigrateAccionToEvent(ActorBase):
    accion_colectiva: AccionesColectivas
    mention: Mention
    event: Event
    default_sector_group: SectorGroup
    need_review: StatusControl

    def __init__(self, accion_colectiva: AccionesColectivas):
        self.accion_colectiva = accion_colectiva
        self.mention = self.get_mention(self.accion_colectiva)
        self.event = self.get_event()
        self.set_location()

        self.default_sector_group, _ = SectorGroup.objects.get_or_create(
            name="Varios", is_collective=True)

        self.need_review, _ = StatusControl.objects.get_or_create(
            name="need_review", group="validation",
            public_name="Requiere revisión")

    def get_event(self) -> Event:
        forma_ac_nombre = getattr(
            self.accion_colectiva.forma_ac, "nombre", None)
        subforma_ac_nombre = getattr(
            self.accion_colectiva.subforma_ac, "nombre", None)

        fecha = getattr(self.accion_colectiva.temporalidad, "fecha", None)
        intervalo = getattr(
            self.accion_colectiva.temporalidad, "intervalo", None)

        if not forma_ac_nombre:
            self.mention.add_comment(
                "YEEKO: Hay un evento (Accion Colectiva) no especificada")
            raise Exception(
                "Forma o Subforma de accion_colectiva no encontrados")

        event_type = EventType.objects.get(name=forma_ac_nombre)
        if not subforma_ac_nombre or subforma_ac_nombre == "NE":
            event_subtype, _ = EventSubtype.objects.get_or_create(
                name=f"No Especificado de {forma_ac_nombre}")
        else:
            event_subtype = EventSubtype.objects.get(name=subforma_ac_nombre)

        event, _ = Event.objects.get_or_create(
            mention=self.mention,
            event_type=event_type,
            event_subtype=event_subtype
        )

        event.date = fecha if not event.date else event.date
        event.duration = intervalo if not event.duration else event.duration
        event.save()
        return event

    def set_involved(self, participant, role_name: str):
        event_role, _ = EventRole.objects.get_or_create(name=role_name)
        Involved.objects.create(
            event=self.event, participant=participant, event_role=event_role,

        )

    def set_location(self):
        ac_to_ubic_query = AccionColectivaToUbicacion.objects\
            .filter(accion_colectiva=self.accion_colectiva)
        for ac_to_ubic in ac_to_ubic_query:
            location = Location.objects.filter(
                ubicacion_id_ref=ac_to_ubic.ubicacion_id).first()  # type: ignore
            if not location:
                continue

            EventLocation.objects.get_or_create(
                event=self.event, location=location
            )

    def migrate_opositor(self, opositor: Opositores):
        opositor_actor, _ = self.get_actor(opositor.nombre)
        participant = self.get_participant(
            opositor_actor, self.mention)
        # se requiere el tipo da participacion, para sustituir Accionante
        self.set_involved(participant, "Accionante")

    def migrate(self):
        opositor_to_ac_query = OpositoresToAC.objects.filter(
            accion_colectiva=self.accion_colectiva)

        for opositor_to_ac in opositor_to_ac_query:
            if not opositor_to_ac.opositor:
                continue
            self.migrate_opositor(opositor_to_ac.opositor)


class AccionesColectivasToEventMigrate:
    errors = []
    events_type: Dict[Any, EventType] = {}

    def __init__(self):
        self.forma_accion_colectiva()
        self.subforma_accion_colectiva()
        for accion_colectiva in AccionesColectivas.objects.all():
            try:
                migrate_accion_colectiva = MigrateAccionToEvent(
                    accion_colectiva)
                migrate_accion_colectiva.migrate()
            except Exception as e:
                self.errors.append([accion_colectiva, e])

    def forma_accion_colectiva(self):
        ac_group, _ = EventGroup.objects.get_or_create(
            name="Acciones Colectivas", model_origin="FormaAC")

        for forma_accion_colectiva in FormaAC.objects.all():
            forma_ac_nombre = forma_accion_colectiva.nombre
            if not forma_ac_nombre:
                continue

            if EventType.objects.filter(name=forma_ac_nombre).exists():
                continue

            sub_forma_exist = SubformaAC.objects.filter(
                id_forma_ac=forma_accion_colectiva.pk).exists()

            event_type = EventType.objects.create(
                name=forma_ac_nombre,
                description=forma_accion_colectiva.descripcion,
                group=ac_group if sub_forma_exist else None
            )
            self.events_type[forma_accion_colectiva.pk] = event_type

    def subforma_accion_colectiva(self):
        for forma in SubformaAC.objects.exclude(nombre="NE"):
            nombre = forma.nombre
            if not nombre:
                continue

            event_subtype, is_created = EventSubtype.objects.get_or_create(
                name=nombre
            )
            if is_created:
                event_subtype.description = forma.descripcion
                event_subtype.save()

            event_type = self.events_type.get(forma.id_forma_ac)
            if not event_type:
                continue

            event_subtype.event_types.add(event_type)
