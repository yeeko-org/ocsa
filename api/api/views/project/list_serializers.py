from rest_framework import serializers

from actor.models import Actor, Participant, Interest
from impact.models import Impact
from project.models import Project, ProjectLocation
from source.models import Mention, Note
from event.models import Event


class ActorBasicSerializer(serializers.ModelSerializer):
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


class LocationSerializer(serializers.ModelSerializer):
    project_location_id = serializers.IntegerField(source='id')
    state = serializers.CharField(source='location.state_id')

    class Meta:
        model = ProjectLocation
        fields = ['state', 'location_id', 'project_location_id']


class ProjectBasicSerializer(serializers.ModelSerializer):
    mentions = MentionSerializer(many=True)
    locations = LocationSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "official_name",
            "description",
            "comments",
            "mentions",
            "megaproject_type",
            "locations",
            "status_validation",
            "status_project",
        ]
