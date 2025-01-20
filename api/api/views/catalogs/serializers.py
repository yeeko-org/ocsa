from rest_framework import serializers

from api.views.project.list_serializers import ImpactSerializer
from impact.models import ImpactSubtype, ImpactType, ImpactGroup, Impact
from source.models import Source
# from project.models import Project
from work_flux.models import StatusControl
# from api.views.actor.serializers import ProjectBaseSerializer

from ps_schema.models import Level, Collection, CollectionLink, FilterGroup


class StatusControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusControl
        fields = "__all__"


class ImpactGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactGroup
        fields = "__all__"


class ImpactSubtypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactSubtype
        fields = "__all__"


class ImpactSubtypeSerializer(serializers.ModelSerializer):
    mentions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ImpactSubtype
        fields = "__all__"


class ImpactSubtypeFullSerializer(serializers.ModelSerializer):
    # impacts = ImpactSerializer(many=True, read_only=True)
    impacts_count = serializers.SerializerMethodField()

    def get_impacts_count(self, obj: ImpactSubtype):
        return Impact.objects.filter(impact_subtype=obj).count()

    class Meta:
        model = ImpactSubtype
        fields = "__all__"


class ImpactTypeSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImpactType
        fields = "__all__"


class ImpactTypeSerializer(serializers.ModelSerializer):
    mentions_count = serializers.IntegerField(read_only=True)
    impact_subtype_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ImpactType
        fields = "__all__"


class ImpactTypeFullSerializer(serializers.ModelSerializer):
    impact_subtypes = ImpactSubtypeSimpleSerializer(many=True, read_only=True)
    impacts_count = serializers.SerializerMethodField()

    def get_impacts_count(self, obj: ImpactType):
        return Impact.objects.filter(impact_type=obj).count()

    class Meta:
        model = ImpactType
        fields = "__all__"


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class SourceFullSerializer(serializers.ModelSerializer):
    notes_count = serializers.ReadOnlyField()

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

