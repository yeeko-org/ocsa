from rest_framework import serializers
from project.models import Project
from source.models import Mention, Note
from impact.models import Impact
from event.models import Event


class  ProjectMiniMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "is_grouper",
            "megaproject_type",
            "parent_project",
        ]


class ProjectMapSerializer(serializers.ModelSerializer):
    conflict_name = serializers.ReadOnlyField(source='conflict.name')
    children_projects_full = ProjectMiniMapSerializer(
        many=True, read_only=True, source='children_projects')
    children_projects = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True)
    # parent_project_full = ProjectMapSerializer(
    #     read_only=True, source='parent_project')
    parent_project_full = serializers.SerializerMethodField()

    def get_parent_project_full(self, obj):
        if obj.parent_project:
            return ProjectMapSerializer(obj.parent_project).data
        return None

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "is_grouper",
            "megaproject_type",
            "conflict_name",
            'children_projects',
            'children_projects_full',
            "parent_project",
            'parent_project_full',
        ]


class NoteMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = [
            "id", "date", "source", "title", "subtitle"
        ]


class MentionMapSerializer(serializers.ModelSerializer):
    note_full = NoteMapSerializer(read_only=True, source='note')

    class Meta:
        model = Mention
        fields = ["id", "note", "note_full", "project"]



class ImpactMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = Impact
        fields = '__all__'


class EventMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'

