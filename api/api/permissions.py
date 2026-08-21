from typing import Any, List, Optional

from rest_framework.permissions import (
    BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly)
from rest_framework.request import Request

from source.models import Note
from space_time.models import Location
from work_flux.models import StatusControl

soft_actions = ["POST", "PATCH"]
# Los FK a StatusControl; `status_project` apunta a otro modelo y queda fuera.
STATUS_FIELDS = [
    "status_register", "status_validation", "status_location", "status_retro"]
# Acciones masivas: son detail=True pero nunca llaman a get_object(), así
# que has_object_permission no corre y el filtro debe aplicarse antes.
BULK_ACTIONS = ["massive_edit", "massive_patch"]


def non_selectable_writes(
        request: Request, obj: Optional[Any] = None) -> List[str]:
    """Status con open_selectable=False que el payload quiere asignar.

    Con `obj` se ignoran los campos que no cambian: permanecer en un
    status no seleccionable siempre se permite; solo se vigila el
    movimiento hacia uno.
    """
    data = request.data
    if not hasattr(data, "get"):
        return []
    wanted = []
    for field in STATUS_FIELDS:
        value = data.get(field)
        if not value or not isinstance(value, str):
            continue
        if obj is not None and getattr(obj, f"{field}_id", None) == value:
            continue
        wanted.append(value)
    if not wanted:
        return []
    return list(StatusControl.objects
                .filter(name__in=wanted, open_selectable=False)
                .values_list("name", flat=True))


class BaseReadOnlyPermission(BasePermission):
    """Base permission that allows read access to everyone"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        if not self.allows_status_target(request, view):
            return False
        return self.has_write_permission(request, view)

    def allows_status_target(
            self, request: Request, view: Any,
            obj: Optional[Any] = None) -> bool:
        """Solo un editor pleno puede asignar un status no seleccionable.

        Sin `obj` (creación o edición masiva) basta con que el payload
        traiga uno; en el detalle se difiere a has_object_permission,
        donde sí puede compararse contra el valor actual.
        """
        if request.user.is_full_editor:
            return True
        is_detail_write = request.method in ["PATCH", "PUT"]
        if obj is None and is_detail_write:
            if getattr(view, "action", None) not in BULK_ACTIONS:
                return True
        return not non_selectable_writes(request, obj)

    def has_write_permission(self, request, view):
        """Override this method in subclasses"""
        raise NotImplementedError


class BaseObjectPermission(BaseReadOnlyPermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        if not self.allows_status_target(request, view, obj):
            return False
        return self.has_write_permission_object(request, view, obj)

    def has_write_permission_object(self, request, view, obj):
        """Override this method in subclasses"""
        raise NotImplementedError

    def has_write_permission(self, request, view):
        return True


class BaseHardPermission(BaseObjectPermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if view.action == "add_file":
            return True
        if request.user.is_anonymous:
            return False
        if not request.user.is_full_editor:
            return False
        return self.has_write_permission_object(request, view, obj)


class IsFullEditorOrReadOnly(BaseReadOnlyPermission):
    def has_write_permission(self, request, view):
        return request.user.is_full_editor


class IsAdminOrReadOnly(BaseReadOnlyPermission):
    def has_write_permission(self, request, view):
        return request.user.is_admin


class ByStatusOrReadOnly(BaseHardPermission):

    def has_write_permission_object(self, request, view, obj: Note):
        if request.method in SAFE_METHODS:
            return True
        if view.action == "add_file":
            return True
        if obj.status_register.open_editor:
            return True

        return request.user.is_full_editor


class IsEditorOrCreateOrRead(BaseHardPermission):

    def has_write_permission_object(self, request, view, obj):

        if request.method in soft_actions and obj.status_validation.open_editor:
            return True

        if obj.status_validation.open_editor:
            return request.user.is_full_editor

        return request.user.is_admin


class DynamicCatalogPermission(BaseHardPermission):

    def has_write_permission_object(self, request, view, obj):

        medium_actions = ["POST", "PATCH", "PUT"]
        if request.method in medium_actions:
            return True

        if obj.status_validation.open_editor:
            return request.user.is_full_editor

        return request.user.is_admin


class LocationPermission(BaseObjectPermission):

    def has_write_permission_object(self, request, view, obj: Location):

        if obj.status_location.open_editor:
            return True

        return request.user.is_admin
