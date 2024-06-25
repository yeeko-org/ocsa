from actor.migrate.common import ActorBase
from impact.models import Impact, ImpactType
from ocsa_legacy.models import (
    AfectacionEcologica, AfectacionSocial, TipoAfectacionEcologica,
    TipoAfectacionSocial)


class AfectacionToImpact(ActorBase):
    def __init__(self, afectacion: AfectacionEcologica | AfectacionSocial) -> None:
        # AfectacionEcologica -> Impact,  descripción_ae --> description
        # AfectacionSocial -> Impact,  descripción_as --> description
        self.afectacion = afectacion
        self.mention = self.get_mention(self.afectacion)
        self.impact_type = self.get_impact_type()

    def get_impact_type(self) -> ImpactType:
        if isinstance(self.afectacion, AfectacionEcologica):
            tipo = self.afectacion.tipo_ae
        else:
            tipo = self.afectacion.tipo_as

        tipo_nombre = getattr(tipo, "nombre")
        return ImpactType.objects.get(name=tipo_nombre)

    def migrate(self) -> None:
        if isinstance(self.afectacion, AfectacionEcologica):
            descripcion_attr = "descripcion_ae"
        else:
            descripcion_attr = "descripcion_as"

        desciption = getattr(self.afectacion, descripcion_attr, None)
        Impact.objects.get_or_create(
            mention=self.mention,
            impact_type=self.impact_type,
            description=desciption
        )


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
            impact_type, is_created = ImpactType.objects.get_or_create(
                name=tipo.nombre
            )

            if is_created:
                impact_type.is_social = False
                impact_type.description = tipo.descripcion
                impact_type.save()

    def tipo_afectacion_social(self) -> None:
        # TipoAfectacionSocial ->  ImpactType con is_social = True
        # tendrá has_subtype = True para los siguientes strings:
        # ["Afectaciones a la salud", "Otros medios de vida afectados"]
        tipo_afectacion_social = TipoAfectacionSocial.objects.all()
        for tipo in tipo_afectacion_social:
            impact_type, is_created = ImpactType.objects.get_or_create(
                name=tipo.nombre
            )

            subtype = [
                "Afectaciones a la salud",
                "Otros medios de vida afectados"]

            if is_created:
                impact_type.is_social = True
                impact_type.description = tipo.descripcion
                impact_type.has_subtype = tipo.nombre in subtype
                impact_type.save()
