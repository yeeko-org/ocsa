from rest_framework import serializers

from api.views.catalogs.serializers import StatusControlSerializer
from api.views.project.list_serializers import (
    MentionSerializer, ProjectBasicSerializer, ProjectMiniSerializer)
from api.views.note.serializers import ParticipantFullSerializer
from project.models import (
    ExtractivismType, MegaprojectType, Project, ProjectFile)
from source.models import Note, Mention
from space_time.models import Location
from api.views.common_serializers import (
    MunicipalitySimpleSerializer,
    LocalitySimpleSerializer, ConflictSerializer)


class ExtractivismTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractivismType
        fields = '__all__'


class LocationFullSerializer(serializers.ModelSerializer):
    municipality_full = MunicipalitySimpleSerializer(
        source='municipality', read_only=True)
    locality_full = LocalitySimpleSerializer(
        source='locality', read_only=True)

    class Meta:
        model = Location
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


class MentionFullSerializer(MentionSerializer):
    note_full = NoteFullSerializer(source='note', read_only=True)
    participants = ParticipantFullSerializer(many=True)

    class Meta:
        model = Mention
        exclude = ['project']


class ProjectFileSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="file.name")
    url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = ProjectFile
        fields = ['id', 'file', 'uploaded_at', 'name', 'url']


class ProjectFullSerializer(ProjectBasicSerializer):
    files = ProjectFileSerializer(many=True, read_only=True)
    conflict_full = ConflictSerializer(read_only=True, source='conflict')
    locations = LocationFullSerializer(many=True, read_only=True)
    extractivism_type = serializers.SerializerMethodField(
        read_only=True)
    mentions = MentionFullSerializer(many=True, read_only=True)
    others_parents_full = ProjectMiniSerializer(
        many=True, read_only=True, source='others_parents')
    children_projects_full = ProjectBasicSerializer(
        many=True, read_only=True, source='children_projects')

    def get_extractivism_type(self, obj):
        return None

    class Meta:
        model = Project
        fields = '__all__'
