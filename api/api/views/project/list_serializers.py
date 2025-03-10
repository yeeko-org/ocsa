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
    main_location = LocationFullSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",  # ID
            "proyecto_id_ref",  # Viejo ID
            "name",  # Nombre
            "alternative_name",  # Nombre alternativo
            "description",  # Descripción
            "parent_project_id",  # ID del proyecto padre
            "conflict",
            "megaproject_type",
            "is_grouper",
            "status_validation",
            "status_project",
            "status_location",
        ]

class ConflictSerializer(ConflictSimpleSerializer):
    projects = ProjectMiniSerializer(many=True, read_only=True)


class ConflictFullSerializer(ConflictSimpleSerializer):
    projects = ProjectBasicSerializer(many=True, read_only=True)
