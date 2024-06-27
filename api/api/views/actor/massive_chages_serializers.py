from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class MassiveChangeSerializer(serializers.Serializer):
    actors_ids = serializers.ListField(child=serializers.IntegerField())
    sector_id = serializers.IntegerField(required=False, allow_null=True)
    status_validation = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    parent_actor_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        any_field = any(
            data.get(field)
            for field in [
                'sector_id', 'status_validation', 'parent_actor_id'
            ])
        if not any_field:
            raise ValidationError(
                'Al menos uno de los campos sector_id, status_validation, o '
                'parent_actor_id es obligatorio.')

        return data
