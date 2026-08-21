"""Delete the physical file when a file-holding row is deleted (task-47)."""
from django.db.models import Model
from django.db.models.signals import post_delete


def _delete_file_on_post_delete(sender: type, instance: Model, **kwargs) -> None:
    file = instance.file
    if not file or not file.name:
        return
    # Two rows can point to the same stored name (legacy imports): only
    # delete the object when no other row still references it.
    still_referenced = sender.objects.filter(
        file=file.name).exclude(pk=instance.pk).exists()
    if still_referenced:
        return
    file.delete(save=False)


def register_file_cleanup(model: type) -> None:
    post_delete.connect(
        _delete_file_on_post_delete, sender=model,
        dispatch_uid=f"file_cleanup_{model._meta.label_lower}")
