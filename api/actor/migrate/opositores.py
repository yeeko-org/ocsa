from typing import Dict
from actor.models import Belong, IndigenousGroup, Sector, SectorGroup
from ocsa_legacy.models import (
    CatSubpoblacionAfectada, FormaOrganizacion, InteresesOpositores,
    Opositores)
from work_flux.models import StatusControl
from actor.migrate.common import ActorBase


class OpositorToActorMigration(ActorBase):
    errors = []
    sectors: Dict[str, Sector] = {}
    belongs: Dict[str, Belong] = {}
    indigenous_groups: Dict[str, IndigenousGroup] = {}

    def __init__(self):
        super().__init__()
        self.default_sg, _ = SectorGroup.objects.get_or_create(
            name="Varios", is_collective=True)

        self.need_review, _ = StatusControl.objects.get_or_create(
            name="need_review", group="validation",
            public_name="Requiere revisión")

        self.set_sectors()
        self.set_belong()
        self.set_indigenous_group()

        opositores = Opositores.objects.all()

        self.need_review, _ = StatusControl.objects.get_or_create(
            name="need_review", group="validation",
            public_name="Requiere revisión")

        for opositor in opositores:
            try:
                self.migrate_to_actor(opositor)
            except Exception as e:
                # raise e
                self.errors.append([opositor, e])

    def set_sectors(self):
        for forma in FormaOrganizacion.objects.all():
            if not forma.nombre:
                continue
            try:
                sector = Sector.objects.get(name=forma.nombre)
            except Sector.DoesNotExist:
                sector = Sector.objects.create(
                    name=forma.nombre, sector_group=self.default_sg)
            self.sectors[forma.nombre] = sector

    def get_sector(self, name: str) -> Sector:
        sector = self.sectors.get(name)
        if not sector:
            sector = Sector.objects.create(
                name=name, sector_group=self.default_sg)
            self.sectors[name] = sector
        return sector

    def set_belong(self):
        data_belong = {
            "is_indigena": "Indígena",
            "is_farmer": "Campesino",
            "is_worker": "Trabajador",
            "is_habitant": "Habitante",
            "is_woman_special": "Mujer",
            "is_affected": "Población Afectada",
        }

        for key, value in data_belong.items():
            belong, _ = Belong.objects.get_or_create(key_name=key, name=value)
            self.belongs[key] = belong

    def get_belong(self, key: str) -> Belong:
        belong = self.belongs.get(key)
        if not belong:
            belong = Belong.objects.create(key_name=key, name=key)
            self.belongs[key] = belong
        return belong

    def set_indigenous_group(self):
        for subpoblacion_afectada in CatSubpoblacionAfectada.objects.all():
            nombre = subpoblacion_afectada.nombre
            if not nombre:
                continue

            indigenous_group, _ = IndigenousGroup.objects.get_or_create(
                name=nombre, description=subpoblacion_afectada.descripcion)
            self.indigenous_groups[nombre] = indigenous_group

    def get_indigenous_group(self, name: str) -> IndigenousGroup:
        indigenous_group = self.indigenous_groups.get(name)
        if not indigenous_group:
            indigenous_group, _ = IndigenousGroup.objects.get_or_create(
                name=name)
            self.indigenous_groups[name] = indigenous_group
        return indigenous_group

    def migrate_to_actor(self, opositor: Opositores):
        if not opositor.nombre:
            return

        opositor_actor, created_actor = self.get_actor(opositor.nombre)
        if opositor.forma_organizacion and opositor.forma_organizacion.nombre:
            opositor_actor.sector = self.get_sector(
                opositor.forma_organizacion.nombre)

        mujer_id = getattr(opositor, "mujer_id", 0) or 0

        if mujer_id > 1:
            opositor_actor.sex = "woman"

        if opositor.pueblo_indigena:
            opositor_actor.indigenous_group = self.get_indigenous_group(
                opositor.pueblo_indigena)

        opositor_actor.save()

        if opositor.is_campesino_or_comunero_or_ejidatario:
            opositor_actor.belongs.add(self.get_belong("is_farmer"))

        if opositor.is_trabajador_empresa:
            opositor_actor.belongs.add(self.get_belong("is_worker"))

        if opositor.is_habitante_zona:
            opositor_actor.belongs.add(self.get_belong("is_habitant"))

        if opositor.is_indigena:
            opositor_actor.belongs.add(self.get_belong("is_indigena"))

        if mujer_id > 2:
            opositor_actor.belongs.add(self.get_belong("is_woman_special"))

        other_opositor = None
        if opositor.otros_opositores and not "*" in opositor.nombre:
            other_name = f"{opositor.nombre} --> {opositor.otros_opositores}"
            other_opositor, created_other = self.get_actor(other_name)
            other_opositor.status_validation = self.need_review
            other_opositor.comments = (
                "YEEKO: Muchos de los nombres de 'otros_opositores' son "
                "demasiado abstractos (y no únicos), por eso todos deben "
                "revisarse")
            other_opositor.save()

        for interes in InteresesOpositores.objects.filter(opositor=opositor):
            mention = self.get_mention(interes)
            self.add_status_project(mention)

            self.add_participant(
                opositor_actor, mention, ["Opositor"], interes.interes)

            if not other_opositor:
                continue
            self.add_participant(
                other_opositor, mention, ["Opositor", "otros_opositores"],
                interes.interes)

        self.register_origin(
            opositor_actor, opositor.pk, "Opositores", created_actor)
        if other_opositor:
            self.register_origin(
                other_opositor, opositor.pk, "Opositores", created_other,
                by="otros_opositores")
