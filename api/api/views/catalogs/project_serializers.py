from rest_framework import serializers

from project.models import MegaprojectType, ExtractivismType, StatusProject

from api.views.project.list_serializers import ProjectBasicSerializer
from api.views.common_serializers import CommonCount


class MegaprojectTypeCountSerializer(CommonCount):

    class Meta:
        model = MegaprojectType
        fields = "__all__"


class MegaprojectTypeFullSerializer(serializers.ModelSerializer):
    projects = ProjectBasicSerializer(many=True)

    class Meta:
        model = MegaprojectType
        fields = "__all__"


class StatusProjectFullSerializer(CommonCount):
    projects_count = serializers.ReadOnlyField()
    status_histories_count = serializers.ReadOnlyField()

    class Meta:
        model = StatusProject
        fields = "__all__"
