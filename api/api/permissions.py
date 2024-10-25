from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsFullEditorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        if request.user.is_superuser or request.user.full_edito:
            return True
