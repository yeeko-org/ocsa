from event.models import EventType, EventSubtype, Event
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Recovery fecha_captura and descripcion_ae from legacy data"

    def handle(self, *args, **kwargs):
        from django.db.models import Count
        events_by_classify = Event.objects.all()\
            .values('event_type', 'event_subtype')\
            .annotate(count=Count('event_type'), count_subtype=Count('event_subtype'))\
            .values('event_type', 'event_subtype', 'count', 'count_subtype')
        print("count", len(events_by_classify))

        for event in events_by_classify:
            description = []
            if event_type := event['event_type']:
                et_name = EventType.objects.get(id=event_type).name
                description.append(et_name)
            if event_subtype := event['event_subtype']:
                es_name = EventSubtype.objects.get(id=event_subtype).name
                description.append(es_name)
            description = " - ".join(description)
            Event.objects.filter(event_type=event_type, event_subtype=event_subtype)\
                .update(description=description)
        print("Finish")





