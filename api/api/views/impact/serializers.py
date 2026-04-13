from rest_framework import serializers
from impact.models import ImpactType


class ImpactTypeSerializer(serializers.ModelSerializer):
    impact_group  = serializers.CharField(
        source='impact_group.name', read_only=True)

    class Meta:
        model = ImpactType
        fields = "__all__"
