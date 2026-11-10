"""Signed comment with the front's convention, dated on the day of the run."""
from django.utils import timezone

AUTHOR = "Ricardo"


def add_comment(obj, text: str) -> bool:
    # The match ignores the date so a rerun on another day stays a no-op.
    if f"- {AUTHOR}: {text}" in (obj.comments or ""):
        return False
    comment = f"{timezone.localdate():%d/%m/%Y} - {AUTHOR}: {text}"
    obj.comments = (
        f"{obj.comments}\n\n{comment}" if obj.comments else comment)
    return True
