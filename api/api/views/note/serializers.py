from rest_framework import serializers

from api.views.project.list_serializers import (
    ImpactSerializer, ParticipantFullSerializer)
from api.views.project.retrieve_serializers import ConflictSerializer
# from api.views.space_time.serializers import LocationSerializer
from api.views.event.serializers import EventSerializer
# from api.views.article.serializers import ArticleDetailSerializer
from project.models import Project, ProjectFile
from source.models import Mention, Note, NoteFile, StatusHistory, Article
from event.models import Event, Involved
from actor.models import Participant, Interest
from impact.models import Impact
from df.models import Displacement
# from impact.models import Impact
from space_time.models import Location
from api.views.common_serializers import ConditionalFieldsMixin


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


class LocationSmallSerializer(ConditionalFieldsMixin):

    class Meta:
        model = Location
        exclude = ['geojson', 'ubicacion_id_ref']


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
    locations = LocationSmallSerializer(many=True, read_only=True)

    def get_extractivism_type(self, obj):
        return None

    class Meta:
        model = Project
        fields = '__all__'


class ExtractivismTypesIdsSerializer(serializers.RelatedField):

    def to_representation(self, value):
        return value.extractivism_types.values_list('id', flat=True)


class ProjectLocationVizSerializer(ConditionalFieldsMixin):
    # extractivism_types = ExtractivismTypesIdsSerializer(
    #     source='megaproject_type', read_only=True)

    # extractivism_types2 = serializers.SerializerMethodField()
    #
    # def get_extractivism_types2(self, obj):
    #     if obj.megaproject_type:
    #         return obj.megaproject_type.extractivism_types.values_list(
    #             'id', flat=True)
    #     return []

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'alternative_name', 'description',
            'megaproject_type', 'is_grouper', 'parent_project'
        ]


class LocationVizSerializer(serializers.ModelSerializer):
    project = ProjectLocationVizSerializer(read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'state', 'municipality', 'locality',
            'latitude', 'longitude', 'type_location', 'geojson',
            'project']


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


class NoteSerializer(ConditionalFieldsMixin):
    mentions = MentionFullSerializer(many=True)

    class Meta:
        model = Note
        fields = '__all__'


class StatusHistoryFullSerializer(serializers.ModelSerializer):
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
        fields = '__all__'


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
