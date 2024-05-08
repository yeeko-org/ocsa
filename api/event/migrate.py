from actor.models import Sector, SectorGroup
from event.models import EventGroup, EventSubtype, EventType
from ocsa_legacy.models import FormaHechoViolencia, HechosViolencia, SectorSocial


class EventoMigrate:
    errors = []

    def __init__(self):
        pass

    def hecho_violencia(self):
        default_group, _ = EventGroup.objects.get_or_create(
            name="Violencia", model_origin="HechosViolencia")
        for h_violencia in HechosViolencia.objects.all():
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
        default_group, _ = SectorGroup.objects.get_or_create(
            name="Varios", is_collective=True)
        special_sectors = [
            "Trabajador de la empresa", "Otro (Abogado opositor)",
            "Periodista", "Abogado", "Activista", "Agente Federal",
            "Activista", "Defensor Ambiental", "Comerciante",
            "Defensor Ambiental", "Profesor", "Comunero",
            "Defensor del territorio", "Comunicador", "Profesora", "Alcalde"
        ]
        for sector_social in SectorSocial.objects.all():
            if Sector.objects.filter(name=sector_social.nombre).exists():
                continue

            sector_group = {}
            if sector_social.nombre in special_sectors:
                sector_group["sector_group"] = default_group

            Sector.objects.create(
                name=sector_social.nombre,
                description=sector_social.descripcion,
                **sector_group
            )
