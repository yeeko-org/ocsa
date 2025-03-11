from rest_framework import serializers

from actor.models import Actor, Participant, Interest
from impact.models import Impact
from project.models import Project, Conflict
from space_time.models import Location
from source.models import Mention, Note
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


class ProjectExportSerializer(serializers.ModelSerializer):
    conflict__id = serializers.ReadOnlyField(source='conflict.id')
    conflict__name = serializers.ReadOnlyField(source='conflict.name')
    conflict__description = serializers.ReadOnlyField(
        source='conflict.description')
    megaproject_type__name = serializers.ReadOnlyField(
        source='megaproject_type.name')
    # megaproject_type__extractivism_types = serializers.ReadOnlyField(
    #     source='megaproject_type.extractivism_types')

    megaproject_type__extractivism_types = serializers.SerializerMethodField()
    parent_project__id = serializers.ReadOnlyField(source='parent_project.id')
    parent_project__name = serializers.ReadOnlyField(
        source='parent_project.name')

    locations__id = serializers.ReadOnlyField()
    locations__state__inegi_code = serializers.ReadOnlyField()
    locations__state__name = serializers.ReadOnlyField()
    locations__municipality__inegi_code = serializers.ReadOnlyField()
    locations__municipality__name = serializers.ReadOnlyField()
    locations__locality__inegi_code = serializers.ReadOnlyField()
    locations__locality__name = serializers.ReadOnlyField()
    locations__latitude = serializers.ReadOnlyField()
    locations__longitude = serializers.ReadOnlyField()

    def get_megaproject_type__extractivism_types(self, obj):
        # TODO: Ricardo revisar si es necesario hacer esta parte por annotate o prefetch_related
        if obj.megaproject_type is None:
            return None
        return ", ".join([str(x) for x in obj.megaproject_type
                          .extractivism_types.values_list('id', flat=True)])

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "alternative_name",
            "description",
            "proyecto_id_ref",

            "conflict__id",
            "conflict__name",
            "conflict__description",
            "megaproject_type__name",
            "megaproject_type__extractivism_types",
            "parent_project__id",
            "parent_project__name",

            "locations__id",
            "locations__state__inegi_code",
            "locations__state__name",
            "locations__municipality__inegi_code",
            "locations__municipality__name",
            "locations__locality__inegi_code",
            "locations__locality__name",
            "locations__latitude",
            "locations__longitude",
        ]


class ConflictSerializer(ConflictSimpleSerializer):
    projects = ProjectMiniSerializer(many=True, read_only=True)


class ConflictFullSerializer(ConflictSimpleSerializer):
    projects = ProjectBasicSerializer(many=True, read_only=True)
