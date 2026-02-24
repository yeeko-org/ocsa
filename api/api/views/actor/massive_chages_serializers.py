from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class MassiveChangeSerializer(serializers.Serializer):
    sector = serializers.IntegerField(required=False, allow_null=True)
    status_validation = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    parent_actor = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        any_field = any(
            data.get(field)
            for field in [
                'sector', 'status_validation', 'parent_actor'
            ])
        if not any_field:
            raise ValidationError(
                'Al menos uno de los campos sector, status_validation, o '
                'parent_actor es obligatorio.')

        return data
