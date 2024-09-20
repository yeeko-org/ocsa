from typing import Dict
from classify.models import Belong, IndigenousGroup, SectorGroup, Sector
from ocsa_legacy.models import (
    CatSubpoblacionAfectada, FormaOrganizacion, InteresesOpositores,
    Opositores)
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

        self.set_sectors()
        self.set_indigenous_group()

        opositores = Opositores.objects.all()

        for opositor in opositores:
            try:
                self.migrate_to_actor(opositor)
            except Exception as e:
                self.errors.append([opositor, e])

    def set_sectors(self):
        for forma in FormaOrganizacion.objects.all():
            if not forma.nombre:
                continue

            sector, _ = Sector.objects.get_or_create(
                name=forma.nombre, defaults={
                    "sector_group": self.default_sg,
                    "status_validation_id": "need_reclassify"})
            self.sectors[forma.nombre] = sector

    def get_sector(self, name: str) -> Sector:
        sector = self.sectors.get(name)
        if not sector:
            sector, _ = Sector.objects.get_or_create(
                name=name, defaults={"sector_group": self.default_sg})
            self.sectors[name] = sector
        return sector

    def get_belong(self, key: str) -> Belong:
        belong = self.belongs.get(key)
        if not belong:
            try:
                belong = Belong.objects.get(key_name=key)
            except Belong.DoesNotExist:
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

        mujer_text = ""
        if mujer_id > 1:
            mujer_text = getattr(opositor.mujer, "nombre", "")
            if mujer_text:
                mujer_text = mujer_text.lower()

        if opositor.pueblo_indigena:
            opositor_actor.indigenous_group = self.get_indigenous_group(
                opositor.pueblo_indigena)

        opositor_actor.save()

        if opositor.is_campesino_or_comunero_or_ejidatario or "campo" in mujer_text:
            opositor_actor.belongs.add(self.get_belong("is_farmer"))

        if opositor.is_trabajador_empresa:
            opositor_actor.belongs.add(self.get_belong("is_worker"))

        if opositor.is_habitante_zona:
            opositor_actor.belongs.add(self.get_belong("is_habitant"))

        if opositor.is_indigena or "indígena" in mujer_text:
            opositor_actor.belongs.add(self.get_belong("is_indigena"))

        if "sobresaliente" in mujer_text:
            opositor_actor.belongs.add(self.get_belong("is_women_special"))

        if "urban" in mujer_text:
            opositor_actor.belongs.add(self.get_belong("is_urban"))

        if "líder" in mujer_text:
            opositor_actor.sex = "woman"
            opositor_actor.belongs.add(self.get_belong("is_leader"))

        if "organización" in mujer_text:
            opositor_actor.belongs.add(
                self.get_belong("is_woman_organization"))

        if "investigadora" in mujer_text:
            opositor_actor.sex = "woman"

        other_opositor = None
        created_other = False
        if opositor.otros_opositores and "*" not in opositor.nombre:
            other_name = f"{opositor.nombre} --> {opositor.otros_opositores}"
            other_opositor, created_other = self.get_actor(other_name)
            other_opositor.status_validation_id = "need_review"  # type: ignore
            other_opositor.comments = (
                "YEEKO: Muchos de los nombres de 'otros_opositores' son "
                "demasiado abstractos (y no únicos), por eso todos deben "
                "revisarse")
            other_opositor.save()

        for interes in InteresesOpositores.objects.filter(opositor=opositor):
            mention = self.get_mention(interes)

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
                field="otros_opositores")
