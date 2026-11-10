"""A user is never deleted while anything of the project points to them.

A pre_delete receiver and not a `delete()` override: the receiver also
runs on queryset and admin deletes. Relations come from `_meta`, so a new
FK or many-to-many to the user is protected without touching this file.
"""
from django.db.models import Model, ProtectedError
from django.db.models.signals import pre_delete

# What Django and DRF attach to any account: deleting the user may take it.
ALLOWED = {"authtoken.token", "admin.logentry", "auth.group",
           "auth.permission"}


def blocking_relations(user: Model) -> list[str]:
    blocking = []
    for field in type(user)._meta.get_fields(include_hidden=True):
        if not field.is_relation:
            continue
        related = field.related_model
        if related._meta.label_lower in ALLOWED:
            continue
        if field.concrete:
            if field.many_to_many and getattr(user, field.name).exists():
                blocking.append(field.name)
            continue
        # The auto-created through table of a many-to-many is reached by
        # the many-to-many relation itself, visible or hidden.
        if related._meta.auto_created:
            continue
        lookup = {field.field.name: user.pk}
        if related._base_manager.filter(**lookup).exists():
            blocking.append(f"{related._meta.label}.{field.field.name}")
    return blocking


def _protect_user(sender: type, instance: Model, **kwargs) -> None:
    if blocking := blocking_relations(instance):
        raise ProtectedError(
            f"El usuario «{instance}» tiene registros asociados "
            f"({', '.join(blocking)}): desactívalo en vez de borrarlo.",
            {instance})


def register_user_guard(user_model: type) -> None:
    pre_delete.connect(
        _protect_user, sender=user_model, dispatch_uid="protect_user")
