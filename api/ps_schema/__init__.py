from __future__ import annotations


def generate_serializer(
        model_cls: type, count_fields: dict | None = None) -> type:
    """
    Auto-generate a ModelSerializer with fields='__all__'.
    If count_fields is provided, a ReadOnlyField() is added for each
    annotation name so that queryset annotations are exposed in the response.
    """
    from rest_framework import serializers
    meta = type('Meta', (), {'model': model_cls, 'fields': '__all__'})
    attrs: dict = {'Meta': meta}
    for ann_name in (count_fields or {}):
        attrs[ann_name] = serializers.ReadOnlyField()
    return type(
        f'{model_cls.__name__}AutoSerializer',
        (serializers.ModelSerializer,),
        attrs,
    )
