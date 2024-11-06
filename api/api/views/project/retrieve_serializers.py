from rest_framework import serializers

from actor.models import Participant
from api.views.catalogs.serializers import StatusControlSerializer
from api.views.project.list_serializers import (
    ImpactSerializer, ActorBasicSerializer)
from project.models import (
    Conflict, ExtractivismType, MegaprojectType, Project, ProjectFile)
from source.models import Note, Mention


class ConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conflict
        fields = '__all__'


class ExtractivismTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractivismType
        fields = '__all__'


class MegaprojectTypeSerializer(serializers.ModelSerializer):
    extractivism_types = ExtractivismTypeSerializer(many=True)
    status_validation = StatusControlSerializer()

    class Meta:
        model = MegaprojectType
        fields = '__all__'


class NoteFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = "__all__"


class ParticipantFullSerializer(serializers.ModelSerializer):
    actor = ActorBasicSerializer()

    class Meta:
        model = Participant
        exclude = ['mention']


class MentionFullSerializer(serializers.ModelSerializer):
    impacts = ImpactSerializer(many=True)
    note = NoteFullSerializer()
    participants = ParticipantFullSerializer(many=True)

    class Meta:
        model = Mention
        exclude = ['project']


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['id', 'file', 'uploaded_at']


class ProjectFullSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True)
    parent_project = serializers.SerializerMethodField()
    conflict = ConflictSerializer()
    extractivism_type = serializers.SerializerMethodField()
    mentions = MentionFullSerializer(many=True)

    def get_parent_project(self, obj):
        if obj.parent_project:
            return ProjectFullSerializer(obj.parent_project).data

    def get_extractivism_type(self, obj):
        return None

    class Meta:
        model = Project
        fields = '__all__'
