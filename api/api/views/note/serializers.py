from rest_framework import serializers

from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantSerializer)
from api.views.project.retrieve_serializers import (
    ConflictSerializer, ProjectFullSerializer)
from api.views.space_time.serializers import LocationSerializer
from api.views.event.serializers import EventSerializer
from project.models import Project, ProjectFile
from source.models import Mention, Note, NoteFile, StatusHistory
from event.models import Event, Involved
from actor.models import Participant, Interest
from impact.models import Impact
# from impact.models import Impact
from space_time.models import Location


class LocationSmallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        exclude = ['geojson', 'ubicacion_id_ref']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectFileSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="file.name")
    url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = ProjectFile
        fields = ['id', 'file', 'uploaded_at', 'name', 'url']


class ProjectSemiFullSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, read_only=True)
    parent_project = serializers.SerializerMethodField(read_only=True)
    conflict_full = ConflictSerializer(read_only=True, source='conflict')
    extractivism_type = serializers.SerializerMethodField()
    locations = LocationSmallSerializer(many=True, read_only=True)

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


class InvolvedFullSerializer(InvolvedSerializer):
    participant_full = ParticipantSerializer(
        source='participant', read_only=True)


class EventSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class EventEmbedSerializer(EventSimpleSerializer):
    involvements = InvolvedSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)


class ImpactEmbedSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Impact
        fields = '__all__'


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
    events = EventEmbedSerializer(many=True)
    impacts = ImpactEmbedSerializer(many=True)


class NoteFileSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="file.name")
    url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = NoteFile
        fields = ['id', 'file', 'uploaded_at', 'name', 'url']


class NoteSerializer(serializers.ModelSerializer):
    mentions = MentionFullSerializer(many=True)

    class Meta:
        model = Note
        fields = '__all__'


class StatusHistoryFullSerializer(serializers.ModelSerializer):
    note_full = NoteSerializer(source='mention.note', read_only=True)

    class Meta:
        model = StatusHistory
        fields = '__all__'


class ImpactFullSerializer(serializers.ModelSerializer):
    note = NoteSerializer(source='mention.note', read_only=True)

    class Meta:
        model = Impact
        fields = '__all__'


class EventFullNoteSerializer(EventEmbedSerializer, EventSerializer):
    note = NoteSerializer(source='mention.note', read_only=True)
    involvements = InvolvedFullSerializer(many=True, read_only=True)

    class Meta:
        model = Event
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

