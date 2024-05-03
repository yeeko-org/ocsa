from ocsa_legacy.models import EstatusProyecto
from space_time.models import StatusProject


class EstatusProyectoToStatusProject:
    errors: list = []

    def __init__(self):
        EstatusProyecto.objects.all().delete()

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
