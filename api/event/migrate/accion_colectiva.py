from typing import Any, Dict, List, Optional
from event.migrate.event_base import EventBase
from actor.models import Participant
from classify.models import SectorGroup, Sector
from event.models import (Event, EventGroup, EventLocation, InvolvedRole,
                          EventSubtype, EventType, Involved)
from ocsa_legacy.models import (
    AccionColectivaToUbicacion, FormaAC, Opositores, OpositoresToAC,
    AccionesColectivas, SubformaAC)
from space_time.models import Location


class MigrateAccionToEvent(EventBase):
    accion_colectiva: AccionesColectivas

    def __init__(self, accion_colectiva: AccionesColectivas):
        self.accion_colectiva = accion_colectiva
        self.mention = self.get_mention(self.accion_colectiva)
        self.event = self.get_main_event()
        ac_to_ubic_query = self.accion_colectiva.accioncolectivatoubicacion_set.all()
        self.set_locations(ac_to_ubic_query)

    def get_main_event(self) -> Event:
        forma_ac_nombre = getattr(
            self.accion_colectiva.forma_ac, "nombre", None)
        subforma_ac_nombre = getattr(
            self.accion_colectiva.subforma_ac, "nombre", None)
        return self.get_event(
            self.accion_colectiva, forma_ac_nombre, subforma_ac_nombre)

    def set_involved(self, participant, role_name: str):
        involved_role, _ = InvolvedRole.objects.get_or_create(name=role_name)
        Involved.objects.create(
            event=self.event, participant=participant,
            involved_role=involved_role,
        )

    def set_not_location(self):
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
        ac_group, created = EventGroup.objects.get_or_create(
            name="Acciones Colectivas", model_origin="FormaAC")
        if created:
            ac_group.icon = 'draw'
            ac_group.color = 'blue'
            ac_group.save()

        for forma_accion_colectiva in FormaAC.objects.all():
            forma_ac_nombre = forma_accion_colectiva.nombre
            if not forma_ac_nombre:
                continue

            if EventType.objects.filter(name=forma_ac_nombre).exists():
                continue

            # sub_forma_exist = SubformaAC.objects.filter(
            #     id_forma_ac=forma_accion_colectiva.pk).exists()

            event_type = EventType.objects.create(
                name=forma_ac_nombre,
                description=forma_accion_colectiva.descripcion,
                event_group=ac_group
            )
            self.events_type[forma_accion_colectiva.pk] = event_type

    def subforma_accion_colectiva(self):
        for forma in SubformaAC.objects.exclude(nombre="NE"):
            nombre = forma.nombre
            if not nombre:
                continue
            if not forma.id_forma_ac:
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
