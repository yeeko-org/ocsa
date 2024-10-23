from rest_framework import serializers

from actor.models import Participant
from api.views.catalogs.serializers import StatusControlSerializer
from api.views.project.list_serializers import (
    ImpactSerializer, ActorBasicSerializer)
from project.models import (
    Conflict, ExtractivismType, MegaprojectType, Project)
from source.models import Note, Mention
from space_time.models import StatusProject


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


class ProjectFullSerializer(serializers.ModelSerializer):
    parent_project = serializers.SerializerMethodField()
    conflict = ConflictSerializer()
    mentions = MentionFullSerializer(many=True)

    def get_parent_project(self, obj):
        if obj.parent_project:
            return ProjectFullSerializer(obj.parent_project).data

    class Meta:
        model = Project
        fields = '__all__'
