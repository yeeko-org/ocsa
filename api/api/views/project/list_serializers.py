from rest_framework import serializers

from actor.models import Actor, Participant, Interest
from impact.models import Impact
from project.models import Project
from space_time.models import Location
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


class LocationFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


class ProjectBasicSerializer(serializers.ModelSerializer):
    mentions = MentionSerializer(many=True, read_only=True)
    locations = LocationFullSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        # fields = "__all__"
        fields = [
            "id",
            "proyecto_id_ref",
            "name",
            "official_name",
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
            "mentions",
            "locations",
        ]
