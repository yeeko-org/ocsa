from .common import ActorBase
from project.models import StatusProject
from source.models import StatusHistory, Mention
from ocsa_legacy.models import EstatusProyectos


class MigrateStatusProject(ActorBase):

    def __init__(self):
        super().__init__()
        StatusHistory.objects.all().delete()
        Mention.objects.all().delete()
        # LUCIAN: Por ahora no debemos usarla, pero siento que es necesario
        # aunque el problema es que eliminaría a sus dependientes
        # self.delete_empty_temporalidad()
        all_estatus_proyectos = EstatusProyectos.objects.all()
        for estatus_proyecto in all_estatus_proyectos:
            self.set_status_project(estatus_proyecto)

    def delete_empty_temporalidad(self):
        from ocsa_legacy.models import Temporalidad, CatTemporalidad
        empty_cats = CatTemporalidad.objects.filter(
            nombre__in=["SD", "NE"])
        Temporalidad.objects.filter(
            fecha__isnull=True,
            intervalo__isnull=True,
            cat_temporalidad__in=empty_cats
        ).delete()

    def get_status(self, estatus_proyecto: EstatusProyectos):
        if estatus_proyecto.estatus and estatus_proyecto.estatus.nombre:
            status_project, _ = StatusProject.objects.get_or_create(
                name=estatus_proyecto.estatus.nombre,
            )
            return status_project
        return None

    def set_status_project(self, estatus_proyecto: EstatusProyectos):

        mention = self.get_mention(estatus_proyecto)
        status_project = self.get_status(estatus_proyecto)
        temporalidad = estatus_proyecto.temporalidad
        type_temporalidad = None
        if temporalidad and temporalidad.cat_temporalidad:
            type_temporalidad = temporalidad.cat_temporalidad.nombre
            if type_temporalidad in ["SD", "NE"]:
                type_temporalidad = None
        if mention:
            StatusHistory.objects.get_or_create(
                mention=mention,
                status_project=status_project,
                date=temporalidad and temporalidad.fecha,
                interval=temporalidad and temporalidad.intervalo,
                type_temporalidad=type_temporalidad,
            )
        if not estatus_proyecto:
            return None

