from typing import Dict, Optional
from actor.models import Belong, IndigenousGroup, Sector, SectorGroup
from ocsa_legacy.models import FormaOrganizacion, InteresesOpositores, Opositores
from work_flux.models import StatusControl
from actor.migrate.common import text_normalizer, ActorBase


class OpositorToActorMigration(ActorBase):
    errors = []
    sectors: Dict[str, Sector] = {}
    belongs: Dict[str, Belong] = {}

    def __init__(self):
        super().__init__()
        self.default_sg, _ = SectorGroup.objects.get_or_create(
            name="Varios", is_collective=True)

        self.set_sectors()
        self.set_belong()

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

    def get_indigenous_group(self, name: str) -> IndigenousGroup:
        indigenous_group, _ = IndigenousGroup.objects.get_or_create(name=name)
        return indigenous_group

    def migrate_to_actor(self, opositor: Opositores):
        # Nombres hambiguos, algunos separados por ;
        # * Vecinos; Trabajadores de la UNAM; Estudiantes de la UNAM de Copilco el Alto, Coyoacán, Ciudad de México (MP115)
        # caracteres especiales como *, y nombres muy generales como "Vecinos"
        opositor_actor = self.get_actor(opositor.nombre)
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
        if opositor.otros_opositores:
            # mismo caso que opositor.nombre
            other_opositor = self.get_actor(opositor.otros_opositores)
        if not other_opositor:
            return

        # se relacionan al final?

        for interes in InteresesOpositores.objects.filter(opositor=opositor):
            # revisar si este es el origen correcto, esta tambien OpositorToNotas y OpositorToProyecto
            mention = self.get_mention(interes)
            self.add_status_project(mention)

            self.add_participant(
                opositor_actor, mention, ["Opositor"], interes.interes)
            self.add_participant(
                other_opositor, mention, ["Opositor", "otros_opositores"],
                interes.interes)
