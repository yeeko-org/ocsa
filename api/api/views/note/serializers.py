from rest_framework import serializers

from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantSerializer)
from api.views.project.retrieve_serializers import (
    ConflictSerializer, ProjectFullSerializer)
from project.models import Project
from source.models import Mention, Note, StatusHistory


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectSemiFullSerializer(serializers.ModelSerializer):
    parent_project = serializers.SerializerMethodField()
    conflict = ConflictSerializer()

    def get_parent_project(self, obj):
        if obj.parent_project:
            return ProjectFullSerializer(obj.parent_project).data

    class Meta:
        model = Project
        fields = '__all__'


class MentionFullSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    impacts = ImpactSerializer(many=True)
    participants = ParticipantSerializer(many=True)

    class Meta:
        model = Mention
        fields = '__all__'


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = '__all__'


class MentionMegaFullSerializer(MentionFullSerializer):
    project = ProjectSemiFullSerializer()
    status_history = StatusHistorySerializer(many=True)


class NoteSerializer(serializers.ModelSerializer):
    mentions = MentionFullSerializer(many=True)

    class Meta:
        model = Note
        fields = '__all__'


class NoteFullSerializer(serializers.ModelSerializer):
    mentions = MentionMegaFullSerializer(many=True)

    class Meta:
        model = Note
        fields = '__all__'


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ['id', 'nota_id_ref', 'old_id']


class NoteEditeSerializer(NoteCreateSerializer):
    pass
