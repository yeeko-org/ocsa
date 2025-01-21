from actor.migrate.common import ActorBase
from impact.models import Impact, ImpactType, ImpactGroup
from ocsa_legacy.models import (
    AfectacionEcologica, AfectacionSocial, TipoAfectacionEcologica,
    TipoAfectacionSocial, AfectacionSocialToUbicacion,
    AfectacionEcologicaToUbicacion)


class AfectacionToImpact(ActorBase):
    impact: Impact | None

    def __init__(self, afectacion: AfectacionEcologica | AfectacionSocial) -> None:
        self.afectacion = afectacion
        self.mention = self.get_mention(self.afectacion)
        self.impact_type = self.get_impact_type()
        self.impact = None

    def get_impact_type(self) -> ImpactType:
        if isinstance(self.afectacion, AfectacionEcologica):
            tipo = self.afectacion.tipo_ae
            group = ImpactGroup.objects.get(is_social=False)
        else:
            group = ImpactGroup.objects.get(is_social=True)
            tipo = self.afectacion.tipo_as

        tipo_nombre = getattr(tipo, "nombre")
        return ImpactType.objects.get(name=tipo_nombre, impact_group=group)

    def migrate(self) -> None:
        is_ae = isinstance(self.afectacion, AfectacionEcologica)
        if is_ae:
            descripcion_attr = "descripcion_ae"
        else:
            descripcion_attr = "descripcion_as"

        description = getattr(self.afectacion, descripcion_attr, None)
        self.impact, _ = Impact.objects.get_or_create(
            mention=self.mention,
            impact_type=self.impact_type,
            description=description
        )
        if is_ae:
            ubicaciones = self.afectacion.afectacionecologicatoubicacion_set.all()
        else:
            ubicaciones = self.afectacion.afectacionsocialtoubicacion_set.all()
        self.set_locations(ubicaciones)

    def set_locations(self, original_locations):
        from space_time.models import Location
        for record_to_ubic in original_locations:
            location = Location.objects.filter(
                ubicacion_id_ref=record_to_ubic.ubicacion_id).first()  # type: ignore
            if not location:
                continue
            location.impact = self.impact
            location.save()


class AfectacionesToImpactMigrate:
    errors = []

    def __init__(self) -> None:
        self.tipo_afectacion_ecologica()
        self.tipo_afectacion_social()

        for afectacion_ecologica in AfectacionEcologica.objects.all():
            try:
                migration = AfectacionToImpact(afectacion_ecologica)
                migration.migrate()
            except Exception as e:
                self.errors.append([afectacion_ecologica, str(e)])

        for afectacion_social in AfectacionSocial.objects.all():
            try:
                migration = AfectacionToImpact(afectacion_social)
                migration.migrate()
            except Exception as e:
                self.errors.append([afectacion_social, str(e)])

    def tipo_afectacion_ecologica(self) -> None:
        # TipoAfectacionEcologica - -> ImpactType con is_social = False
        tipo_afectacion_ecologica = TipoAfectacionEcologica.objects.all()
        for tipo in tipo_afectacion_ecologica:
            self.save_impact_type(False, tipo.nombre)

    def tipo_afectacion_social(self) -> None:
        tipo_afectacion_social = TipoAfectacionSocial.objects.all()
        for tipo in tipo_afectacion_social:
            self.save_impact_type(True, tipo.nombre)

    def save_impact_type(self, is_social: bool, name: str) -> None:
        impact_group = ImpactGroup.objects.get(is_social=is_social)
        # subtype = [
        #     "Afectaciones a la salud",
        #     "Otros medios de vida afectados"]

        ImpactType.objects.get_or_create(
            name=name,
            # is_social=is_social,
            impact_group=impact_group,
            # has_subtype=name in subtype
        )
