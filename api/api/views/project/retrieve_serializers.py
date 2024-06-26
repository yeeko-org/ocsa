from rest_framework import serializers

from actor.models import Actor, Participant
from api.views.catalogs.serializers import StatusControlSerializer
from api.views.project.list_serializers import ImpactSerializer
from project.models import (
    Conflict, DeploymentCapitalType, MegaprojectType, Project, Scale)
from source.models import Note
from space_time.models import StatusProject


class ConflictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conflict
        fields = '__all__'


class DeploymentCapitalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentCapitalType
        fields = '__all__'


class MegaprojectTypeSerializer(serializers.ModelSerializer):
    deployment_capital_types = DeploymentCapitalTypeSerializer(many=True)
    status_validation = StatusControlSerializer()

    class Meta:
        model = MegaprojectType
        fields = '__all__'


class ScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scale
        fields = '__all__'


class StatusProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusProject
        fields = '__all__'


class NoteFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = "__all__"


class ActorFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        exclude = ['std_name', 'capital_id_ref']


class ParticipantFullSerializer(serializers.ModelSerializer):
    actor = ActorFullSerializer()

    class Meta:
        model = Participant
        exclude = ['mention']


class MentionFullSerializer(serializers.ModelSerializer):
    impacts = ImpactSerializer(many=True)
    note = NoteFullSerializer()
    participants = ParticipantFullSerializer(many=True)


class ProjectFullSerializer(serializers.ModelSerializer):
    parent_project = serializers.SerializerMethodField()
    conflict = ConflictSerializer()
    megaproject_type = MegaprojectTypeSerializer()
    scale = ScaleSerializer()
    status_project = StatusProjectSerializer()
    status_register = StatusControlSerializer()
    mentions = MentionFullSerializer(many=True)

    def get_parent_project(self, obj):
        if obj.parent_project:
            return ProjectFullSerializer(obj.parent_project).data

    class Meta:
        model = Project
        fields = '__all__'
