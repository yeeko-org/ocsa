from rest_framework import serializers
from project.models import Project
from source.models import Mention, Note, StatusHistory
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
    source_name = serializers.ReadOnlyField(source='source.name')

    class Meta:
        model = Note
        fields = [
            "id", "date", "source", "source_name", "title", "subtitle"
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
        fields = [
            "id", "mention", "event_type", "purpose", "date",
            "description", "number_women", "number_men", "number_mix",
        ]


class StatusHistoryMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusHistory
        fields = ["id", "status_project", "date"]


class MentionDeepMapSerializer(serializers.ModelSerializer):
    """Mención con su proyecto + impactos/eventos/historial anidados.
    Usado como nested dentro de NoteDeepMapSerializer (note_map root).
    """
    project_full = ProjectMiniMapSerializer(read_only=True, source='project')
    status_history = StatusHistoryMapSerializer(many=True, read_only=True)
    impacts = ImpactMapSerializer(many=True, read_only=True)
    events = EventMapSerializer(many=True, read_only=True)

    class Meta:
        model = Mention
        fields = [
            "id", "project", "project_full",
            "status_history", "impacts", "events",
        ]


class NoteDeepMapSerializer(NoteMapSerializer):
    """Root del endpoint note_map: metadatos de nota + menciones deep.
    Hereda de NoteMapSerializer (mismo set de campos base) y agrega
    `mentions`. La separación evita un loop de recursión cuando
    NoteMapSerializer se usa como nested dentro de MentionMapSerializer
    en el endpoint project_map.
    """
    mentions = MentionDeepMapSerializer(many=True, read_only=True)

    class Meta(NoteMapSerializer.Meta):
        fields = NoteMapSerializer.Meta.fields + ["mentions"]

