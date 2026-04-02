from rest_framework import serializers

from impact.models import ImpactSubtype, ImpactType, Impact
from work_flux.models import StatusControl


class StatusControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusControl
        fields = "__all__"


class ImpactSubtypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactSubtype
        fields = "__all__"


class ImpactTypeFullSerializer(serializers.ModelSerializer):
    impact_subtypes = ImpactSubtypeSimpleSerializer(many=True, read_only=True)
    impacts_count = serializers.SerializerMethodField()

    def get_impacts_count(self, obj: ImpactType):
        return Impact.objects.filter(impact_type=obj).count()

    class Meta:
        model = ImpactType
        fields = "__all__"
