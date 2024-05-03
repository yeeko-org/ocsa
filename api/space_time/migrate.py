from ocsa_legacy.models import EstatusProyecto
from space_time.models import StatusProject


class EstatusProyectosToStatusProject:
    errors: list = []

    def __init__(self):

        for estatus in EstatusProyecto.objects.all():
            try:
                status, _ = StatusProject.objects.get_or_create(
                    name=estatus.nombre
                )
                if estatus.descripcion:
                    status.description = estatus.descripcion
                    status.save()
            except Exception as e:
                self.errors.append([estatus, e])
