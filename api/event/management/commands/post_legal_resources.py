from django.core.management.base import BaseCommand


from event.models import Event, Purpose, EventType
from impact.models import Impact


class Command(BaseCommand):
    help = 'Migración de Modelos Legacy a Events'
    purpose_pro = Purpose.objects.get(name="Defensa")
    purpose_against = Purpose.objects.get(name="Despojo")

    def handle(self, *args, **kwargs):

        print("Deleting old events")
        equivalences = [
            {
                "impact_type_name": "Mecanismos legales del despojo",
                "event_type_name": "Variado (despojo)",
                "purpose": self.purpose_against
            },
            {
                "impact_type_name": "Mecanismos legales para la defensa",
                "event_type_name": "Variado (defensa)",
                "purpose": self.purpose_pro
            },
            {
                "impact_type_name": "MIA",
                "event_type_name": "Manifestación de Impacto Ambiental (MIA)",
                "purpose": self.purpose_against
            },
            {
                "impact_type_name": "Consulta libre, previa e informada",
                "event_type_name": "Consulta Libre, Previa e Informada (CLPI)",
                "purpose": self.purpose_against
            }
        ]
        for equivalence in equivalences:

            self.migrate_impacts(
                equivalence["impact_type_name"],
                equivalence["event_type_name"],
                equivalence["purpose"]
            )

    def migrate_impacts(self, impact_type_name, event_type_name, purpose):
        origin_impacts = Impact.objects\
            .filter(impact_type__name=impact_type_name)
        print(f"Starting Impact migration with {origin_impacts.count()} impacts")
        event_type = EventType.objects.get(name=event_type_name)
        for impact in origin_impacts:
            event, _ = Event.objects.get_or_create(
                description=impact.description,
                purpose=purpose,
                event_type=event_type,
                mention=impact.mention,
            )
            impact.locations.update(event=event, impact=None)

        origin_impacts.delete()
