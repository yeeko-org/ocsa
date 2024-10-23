from actor.migrate.common import ActorBase
from source.models import Mention
from event.models import Event
from classify.models import SectorGroup, Sector
from work_flux.models import StatusControl
from event.models import EventType, EventSubtype, EventGroup
from ocsa_legacy.models import Violencia


class EventBase(ActorBase):
    mention: Mention
    event: Event
    default_sector_group = SectorGroup.objects.get(name="Varios")
    need_review: StatusControl = StatusControl.objects.get(name="need_review")

    def get_event(self, main_model, event_type_name, event_subtype_name):
        fecha = getattr(main_model.temporalidad, "fecha", None)
        intervalo = getattr(main_model.temporalidad, "intervalo", None)
        is_violencia = isinstance(main_model, Violencia)
        group_name = "Violencia" if is_violencia else "Acciones Colectivas"
        if not event_type_name and not event_subtype_name:
            group = "Violencia" if is_violencia else "Accion Colectiva"
            self.mention.add_comment(
                f"YEEKO: Hay un evento ({group}) no especificado")
            complement = "Hecho de violencia" if is_violencia \
                else "Accion Colectiva"
            raise Exception(f"{complement} no encontrado")
        if not event_type_name:
            event_type_name = f"No Especificado de {group_name}"

        event_type, created = EventType.objects.get_or_create(
            name=event_type_name)
        if created:
            event_type.event_group = EventGroup.objects.get(name=group_name)
            event_type.save()
        if not event_subtype_name or event_subtype_name == "NE":
            event_subtype, _ = EventSubtype.objects.get_or_create(
                name=f"No Especificado de {event_type_name}")
        else:
            event_subtype, _ = EventSubtype.objects.get_or_create(
                name=event_subtype_name)

        event_subtype.event_types.add(event_type)
        event_subtype.save()

        event, _ = Event.objects.get_or_create(
            mention=self.mention,
            event_type=event_type,
            event_subtype=event_subtype
        )

        event.date = fecha if not event.date else event.date
        event.duration = intervalo if not event.duration else event.duration
        event.save()
        return event

    def set_locations(self, original_locations):
        from space_time.models import Location
        from event.models import EventLocation
        for record_to_ubic in original_locations:
            location = Location.objects.filter(
                ubicacion_id_ref=record_to_ubic.ubicacion_id).first()  # type: ignore
            if not location:
                continue

            EventLocation.objects.get_or_create(
                event=self.event, location=location
            )

