from rest_framework import serializers

from project.models import Project


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['id', 'proyecto_id_ref', 'legacy_id_mp']


class ProjectEditSerializer(ProjectCreateSerializer):
    pass
