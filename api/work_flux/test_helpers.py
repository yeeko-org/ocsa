"""Ayudantes compartidos para armar status en las suites."""

from api.permissions import status_fields
from work_flux.models import StatusControl, StatusGroup


GROUP_NAMES = {
    "register": "Registro",
    "validation": "Validación",
    "location": "Ubicación",
    "retro": "Feedback",
}


def make_status(name: str, group: str, **kwargs) -> StatusControl:
    """Crea un StatusControl trayendo su grupo si aún no existe.

    El grupo es un FK desde 0008, así que ninguna suite puede crear un
    status sin sembrarlo antes; esto evita repetir el get_or_create en
    cada setUpTestData.
    """
    status_group, created = StatusGroup.objects.get_or_create(
        key_name=group,
        defaults={"public_name": GROUP_NAMES.get(group, group)})
    # El caché de status_fields() es por proceso: un grupo nuevo a mitad
    # de la corrida no se vería sin esto.
    if created:
        status_fields.cache_clear()
    return StatusControl.objects.create(
        name=name, group=status_group, **kwargs)
