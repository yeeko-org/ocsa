
from rest_framework import serializers
from ps_schema.models import Collection


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = [
            'snake_name', 'level', 'order', 'icon', 'color',
            'help_text', 'description',
        ]
