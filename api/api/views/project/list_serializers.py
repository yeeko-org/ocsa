from rest_framework import serializers

from actor.models import Actor, Participant, Interest
from impact.models import Impact
from project.models import Project, Conflict, MegaprojectType
from space_time.models import Location
from source.models import Mention, Note
from api.views.common_serializers import BaseExportSerializer
from event.models import Event


class ActorBasicSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()

    def get_participants_count(self, obj):
        return 9999

    class Meta:
        model = Actor
        exclude = ['std_name', 'capital_id_ref']


class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = '__all__'


class ParticipantSerializer(serializers.ModelSerializer):
    actor_full = ActorBasicSerializer(source='actor')
    interests = InterestSerializer(many=True)

    class Meta:
        model = Participant
        fields = "__all__"


class ImpactSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impact
        fields = '__all__'
        read_only_fields = ['mention']


class ImpactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Impact
        fields = '__all__'


class NoteBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ['id', 'title', 'source', 'date']


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['event_type', 'event_subtype',
                  'date', 'duration', 'description']


class MentionSerializer(serializers.ModelSerializer):
    impacts = ImpactSerializer(many=True)
    participants = ParticipantSerializer(many=True)
    note = NoteBasicSerializer()
    events = EventSerializer(many=True)

    class Meta:
        model = Mention
        exclude = ['project']


class LocationFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


class ProjectMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'


class ConflictSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conflict
        fields = '__all__'


class ProjectBasicSerializer(serializers.ModelSerializer):
    mentions = MentionSerializer(many=True, read_only=True)
    locations = LocationFullSerializer(many=True, read_only=True)
    conflict_full = ConflictSimpleSerializer(read_only=True, source='conflict')
    children_projects = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True)
    parent_project_full = ProjectMiniSerializer(
        read_only=True, source='parent_project')

    class Meta:
        model = Project
        # fields = "__all__"
        fields = [
            "id",
            "proyecto_id_ref",
            "name",
            "alternative_name",
            "description",
            "comments",
            "parent_project",
            # "other_parents",
            "conflict",
            "conflict_full",
            "megaproject_type",
            "is_grouper",
            "status_validation",
            "status_project",
            "status_location",
            "mentions",
            "locations",
            "children_projects",
            "parent_project_full"
        ]


class ProjectMiniBasicSerializer(serializers.ModelSerializer):
    locations = LocationFullSerializer(many=True, read_only=True)
    parent_project_full = ProjectMiniSerializer(
        read_only=True, source='parent_project')

    class Meta:
        model = Project
        # fields = "__all__"
        fields = [
            "id",
            "proyecto_id_ref",
            "name",
            "alternative_name",
            "description",
            "comments",
            "parent_project",
            # "other_parents",
            "conflict",
            "megaproject_type",
            "is_grouper",
            "status_validation",
            "status_project",
            "status_location",
            "locations",
            "parent_project_full"
        ]


class ExtractivismTypesSerializer(serializers.RelatedField):

    def to_representation(self, value):
        return ", ".join(value.extractivism_types.values_list('name', flat=True))


class MegaprojectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MegaprojectType
        fields = "__all__"


class ProjectExportSerializer(BaseExportSerializer):
    conflict = ConflictSimpleSerializer()
    # conflict__id = serializers.ReadOnlyField(source='conflict.id')
    # conflict__name = serializers.ReadOnlyField(source='conflict.name')
    # conflict__description = serializers.ReadOnlyField(
    #     source='conflict.description')
    # megaproject_type__name = serializers.ReadOnlyField(
    #     source='megaproject_type.name')
    megaproject_type = MegaprojectTypeSerializer()
    extractivism_types = ExtractivismTypesSerializer(
        source='megaproject_type', read_only=True)
    parent_project = ProjectMiniSerializer()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "alternative_name",
            "description",
            "proyecto_id_ref",

            "conflict",
            "megaproject_type",
            "extractivism_types",
            "parent_project",

            "location_id",
            "state__inegi_code",
            "state__short_name",
            "municipality__inegi_code",
            "municipality__name",
            "locality__inegi_code",
            "locality__name",
            "latitude",
            "longitude",
        ]


class ConflictSerializer(ConflictSimpleSerializer):
    projects = ProjectMiniSerializer(many=True, read_only=True)


class ConflictFullSerializer(ConflictSimpleSerializer):
    projects = ProjectBasicSerializer(many=True, read_only=True)


class ImpactExportSerializer(serializers.ModelSerializer):
    pass

