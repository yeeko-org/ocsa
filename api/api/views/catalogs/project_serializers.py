from rest_framework import serializers

from project.models import MegaprojectType, ExtractivismType

from api.views.project.list_serializers import ProjectBasicSerializer
from api.views.catalogs.serializers import CommonCount


class ExtractivismTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractivismType
        fields = "__all__"


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

