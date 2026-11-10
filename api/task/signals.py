"""Write `ClickHistory.deleted_origin` before a clicked record is deleted.

pre_delete runs before the Collector nulls the FKs, so the clicks can
still be found by the FK that is about to go null.
"""
from django.db.models import Model
from django.db.models.signals import pre_delete

from task.deleted_origin import build_origin, label_for

TRACKED_FIELDS = ("note", "article", "project", "location")


def _project_name(location: Model, origin: object) -> str | None:
    # On a project cascade the deleted project arrives as `origin`, and it
    # is still in the database: no query per location.
    if isinstance(origin, Model) and origin._meta.model_name == "project" \
            and origin.pk == location.project_id:
        return origin.name
    from project.models import Project
    return Project.objects.filter(pk=location.project_id) \
        .values_list("name", flat=True).first()


def _trace_clicks(
        sender: type, instance: Model, origin: object = None,
        **kwargs) -> None:
    from task.models import ClickHistory
    model_name = sender._meta.model_name
    clicks = ClickHistory.objects.filter(**{model_name: instance.pk})
    extra = None
    if model_name == "location" and instance.project_id:
        # The name costs a query: only for locations that have clicks.
        if not clicks.exists():
            return
        extra = {"project_id": instance.project_id,
                 "project_name": _project_name(instance, origin)}
    clicks.update(deleted_origin=build_origin(
        model_name, instance.pk, label_for(model_name, instance), extra))


def register_click_trace() -> None:
    from task.models import ClickHistory
    for field_name in TRACKED_FIELDS:
        model = ClickHistory._meta.get_field(field_name).related_model
        pre_delete.connect(
            _trace_clicks, sender=model,
            dispatch_uid=f"click_trace_{model._meta.label_lower}")
