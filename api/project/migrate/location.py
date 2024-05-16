

from ocsa_legacy.models import Proyecto, ProyectoToUbicacion
from project.models import Project, ProjectLocation
from space_time.models import Location


class ProyectoToUbicacionMigrate:
    def __init__(self):
        for proy_to_ubic in ProyectoToUbicacion.objects.all():
            proyecto_id = proy_to_ubic.proyecto_id  # type: ignore
            ubicacion_id = proy_to_ubic.ubicacion_id  # type: ignore

            if not (proyecto_id and ubicacion_id):
                continue

            project = Project.objects.filter(
                proyecto_id_ref=proyecto_id).first()
            location = Location.objects.filter(
                ubicacion_id_ref=ubicacion_id).first()

            if not (project and location):
                continue

            ProjectLocation.objects.get_or_create(
                project=project, location=location
            )
