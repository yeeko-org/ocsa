from rest_framework import serializers

from project.models import MegaprojectType, ExtractivismType, StatusProject

from api.views.project.list_serializers import ProjectBasicSerializer
from api.views.common_serializers import CommonCount


class MegaprojectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MegaprojectType
        fields = "__all__"


class MegaprojectTypeCountSerializer(CommonCount):

    class Meta:
        model = MegaprojectType
        fields = "__all__"


class MegaprojectTypeFullSerializer(MegaprojectTypeSerializer):
    projects = ProjectBasicSerializer(many=True)

    class Meta:
        model = MegaprojectType
        fields = "__all__"


class ExtractivismTypeSerializer(serializers.ModelSerializer):
    # megaproject_types = MegaprojectTypeCountSerializer(
    #     many=True, read_only=True)
    megaproject_types_count = serializers.SerializerMethodField()

    def get_megaproject_types_count(self, obj):
        return obj.megaproject_types.count()

    class Meta:
        model = ExtractivismType
        fields = "__all__"


class ExtractivismTypeFullSerializer(serializers.ModelSerializer):
    megaproject_types = MegaprojectTypeCountSerializer(many=True)

    class Meta:
        model = ExtractivismType
        fields = "__all__"


class StatusProjectSerializer(CommonCount):

    class Meta:
        model = StatusProject
        fields = "__all__"
