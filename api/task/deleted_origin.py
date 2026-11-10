"""Trace left on a click when the record it points to is deleted.

The label is built only from the record's own columns: by the time the
trace is written the record is being deleted, and a relation (the state
of a location, the source of a note) may already be gone or cost a query
per row inside a cascade.
"""
from typing import Any

from django.utils import timezone

LABEL_MAX = 255


def location_label(
        latitude: float | None, longitude: float | None,
        details: str | None) -> str:
    if latitude and longitude:
        return f"{latitude}, {longitude}"
    return details or "Ubicación sin coordenadas ni detalles"


def label_for(model_name: str, obj: Any) -> str:
    if model_name == "location":
        label = location_label(obj.latitude, obj.longitude, obj.details)
    elif model_name == "article":
        label = f"{obj.uid} - {obj.title or 'sin título'}"
    elif model_name == "project":
        label = obj.name or "Proyecto sin nombre"
    else:
        label = obj.title
    return (label or "")[:LABEL_MAX]


def build_origin(
        model_name: str, pk: int, label: str,
        extra: dict | None = None) -> dict:
    return {
        "model": model_name,
        "id": pk,
        "label": label,
        **(extra or {}),
        "date": timezone.now().isoformat(timespec="seconds"),
    }
