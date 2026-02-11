from rest_framework import serializers

from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantFullSerializer)
from api.views.project.retrieve_serializers import ConflictSerializer
from api.views.event.serializers import EventSerializer
from api.views.common_serializers import (
    ConditionalFieldsMixin, MunicipalitySimpleSerializer,
    LocalitySimpleSerializer)

from project.models import Project, ProjectFile
from source.models import Mention, Note, NoteFile, StatusHistory, Article
from event.models import Event, Involved
from actor.models import Participant, Interest
from impact.models import Impact
from df.models import Displacement
from space_time.models import Location, Municipality, Locality


# class ConditionalFieldsSerializerMixin:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         request = self.context.get('request')
#         if request and not request.user.is_authenticated:
#             restricted_fields = getattr(self.Meta, 'restricted_fields', ['status_register', 'comments'])
#             for field_name in restricted_fields:
#                 self.fields.pop(field_name, None)
#
#
# class BaseModelSerializer(ConditionalFieldsSerializerMixin, serializers.ModelSerializer):
#     pass


class LocationSimpleSerializer(ConditionalFieldsMixin):
    class Meta:
        model = Location
        fields = '__all__'


class DisplacementSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = '__all__'


class LocationSemiFullSerializer(ConditionalFieldsMixin):
    municipality_full = MunicipalitySimpleSerializer(
        source='municipality', read_only=True)
    locality_full = LocalitySimpleSerializer(
        source='locality', read_only=True)

    class Meta:
        model = Location
        # exclude = ['geojson', 'ubicacion_id_ref']
        fields = [
            "id", "project", "state", "municipality", "municipality_full",
            "locality", "locality_full", "details",
            "type_location", "status_location"]


class ProjectSerializer(ConditionalFieldsMixin):

    class Meta:
        model = Project
        fields = '__all__'


class ProjectFileSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="file.name")
    url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = ProjectFile
        fields = ['id', 'file', 'uploaded_at', 'name', 'url']


class ProjectSemiFullSerializer(ConditionalFieldsMixin):
    files = ProjectFileSerializer(many=True, read_only=True)
    parent_project_full = ProjectSerializer(
        read_only=True, source='parent_project')
    conflict_full = ConflictSerializer(read_only=True, source='conflict')
    extractivism_type = serializers.SerializerMethodField()
    locations = LocationSemiFullSerializer(many=True, read_only=True)

    def get_extractivism_type(self, obj):
        return None

    class Meta:
        model = Project
        fields = '__all__'


class ExtractivismTypesIdsSerializer(serializers.RelatedField):

    def to_representation(self, value):
        return value.extractivism_types.values_list('id', flat=True)


class InvolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Involved
        fields = '__all__'


class InvolvedFullSerializer(InvolvedSerializer):
    participant_full = ParticipantFullSerializer(
        source='participant', read_only=True)


class EventSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class EventEmbedSerializer(ConditionalFieldsMixin, EventSimpleSerializer):
    involvements = InvolvedSerializer(many=True, read_only=True)
    locations = LocationSimpleSerializer(many=True, read_only=True)
    displacements = DisplacementSimpleSerializer(many=True, read_only=True)


class ImpactEmbedSerializer(serializers.ModelSerializer):
    locations = LocationSimpleSerializer(many=True, read_only=True)
    displacements = DisplacementSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Impact
        fields = '__all__'


class MentionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mention
        fields = '__all__'


class MentionFullSerializer(ConditionalFieldsMixin):
    project_full = ProjectSerializer(
        source='project', read_only=True)
    impacts = ImpactSerializer(many=True)
    participants = ParticipantFullSerializer(many=True)
    events = EventSimpleSerializer(many=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Mention
        fields = '__all__'


class StatusSimpleHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusHistory
        fields = '__all__'


class StatusHistorySerializer(StatusSimpleHistorySerializer):
    project_full = ProjectSerializer(
        source='mention.project', read_only=True)


class MentionMegaFullSerializer(MentionFullSerializer):
    project_full = ProjectSemiFullSerializer(
        source='project', read_only=True)
    # project = ProjectSemiFullSerializer()
    status_history = StatusSimpleHistorySerializer(many=True)
    events = EventEmbedSerializer(many=True)
    impacts = ImpactEmbedSerializer(many=True)


class NoteFileSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="file.name")
    url = serializers.ReadOnlyField(source="file.url")

    class Meta:
        model = NoteFile
        fields = ['id', 'file', 'uploaded_at', 'name', 'url']


class NoteSerializer(ConditionalFieldsMixin):
    mentions = MentionFullSerializer(many=True)

    class Meta:
        model = Note
        exclude = ['pre_mentions', 'link', 'nota_id_ref']


class StatusHistoryFullSerializer(serializers.ModelSerializer):
    project_full = ProjectSerializer(
        source='mention.project', read_only=True)
    note_full = NoteSerializer(source='mention.note', read_only=True)

    class Meta:
        model = StatusHistory
        fields = '__all__'


class ImpactFullSerializer(ImpactEmbedSerializer):
    note = NoteSerializer(source='mention.note', read_only=True)

    class Meta:
        model = Impact
        fields = '__all__'


class EventFullNoteSerializer(EventEmbedSerializer, EventSerializer):
    note = NoteSerializer(source='mention.note', read_only=True)
    involvements = InvolvedFullSerializer(many=True, read_only=True)
    event_group = serializers.IntegerField(
        source='event_type.event_group_id', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class ArticleSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        exclude = [
            'pre_capture', 'basic_content', 'metadata',
            'html_content', 'content', 'errors']


class NoteFullSerializer(ConditionalFieldsMixin):
    files = NoteFileSerializer(many=True, read_only=True)
    mentions = MentionMegaFullSerializer(many=True, read_only=True)
    articles = ArticleSimpleSerializer(read_only=True, many=True)

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


class PreMentionSerializer(serializers.Serializer):
    path = serializers.CharField(required=True)
    discarded = serializers.BooleanField(required=True)
    element_id = serializers.IntegerField(required=False)

