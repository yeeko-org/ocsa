from rest_framework import serializers

from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantSerializer)
from api.views.project.retrieve_serializers import (
    ConflictSerializer, ProjectFullSerializer)
from project.models import Project
from source.models import Mention, Note, NoteFile, StatusHistory
from event.models import Event, Involved
from actor.models import Participant, Interest
# from impact.models import Impact


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectSemiFullSerializer(serializers.ModelSerializer):
    parent_project = serializers.SerializerMethodField(read_only=True)
    conflict = ConflictSerializer(read_only=True)
    extractivism_type = serializers.SerializerMethodField()

    def get_parent_project(self, obj):
        if obj.parent_project:
            return ProjectFullSerializer(obj.parent_project).data

    def get_extractivism_type(self, obj):
        return None

    class Meta:
        model = Project
        fields = '__all__'


class InvolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Involved
        fields = '__all__'


class EventSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class EventSerializer(EventSimpleSerializer):
    involvements = InvolvedSerializer(many=True)


class MentionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mention
        fields = '__all__'


class MentionFullSerializer(serializers.ModelSerializer):
    project_full = ProjectSerializer(
        source='project', read_only=True)
    impacts = ImpactSerializer(many=True)
    participants = ParticipantSerializer(many=True)
    events = EventSimpleSerializer(many=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Mention
        fields = '__all__'


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = '__all__'


class MentionMegaFullSerializer(MentionFullSerializer):
    project_full = ProjectSemiFullSerializer(
        source='project', read_only=True)
    # project = ProjectSemiFullSerializer()
    status_history = StatusHistorySerializer(many=True)
    events = EventSerializer(many=True)


class NoteFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteFile
        fields = ['id', 'file', 'uploaded_at']


class NoteSerializer(serializers.ModelSerializer):
    mentions = MentionFullSerializer(many=True)

    class Meta:
        model = Note
        fields = '__all__'


class NoteFullSerializer(serializers.ModelSerializer):
    files = NoteFileSerializer(many=True, read_only=True)
    mentions = MentionMegaFullSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = '__all__'


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ['id', 'nota_id_ref', 'old_id']


class ParticipantSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'

