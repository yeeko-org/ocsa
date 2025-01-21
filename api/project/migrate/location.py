

from ocsa_legacy.models import  ProyectoToUbicacion
from project.models import Project
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

            if not (project.exists() and location.exists()):
                # print(f"Project or Location not found: {proyecto_id}, {ubicacion_id}")
                continue
            location.project = project
            location.save()

            # ProjectLocation.objects.get_or_create(
            #     project=project, location=location
            # )
