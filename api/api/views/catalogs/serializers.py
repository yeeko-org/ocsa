from rest_framework import serializers

from impact.models import ImpactSubtype, ImpactType, ImpactGroup
from source.models import Source
from work_flux.models import StatusControl

from space_time.models import StatusProject

from ps_schema.models import Level, Collection, CollectionLink, FilterGroup


class CommonCount(serializers.ModelSerializer):
    count = serializers.ReadOnlyField()


class StatusProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusProject
        fields = "__all__"


class StatusControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusControl
        fields = "__all__"


class ImpactGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactGroup
        fields = "__all__"


class ImpactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactType
        fields = "__all__"


class ImpactSubtypeSerializer(serializers.ModelSerializer):
    # impact_type = ImpactTypeSerializer()

    class Meta:
        model = ImpactSubtype
        fields = "__all__"




class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionLink
        fields = "__all__"


class FilterGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterGroup
        fields = "__all__"

