from rest_framework import serializers

from actor.models import Actor, OriginReference, Participant
from project.models import Project
from source.models import Mention, Note
from space_time.models import Location

from api.views.note.serializers import NoteBasicSerializer


class ActorBasicSerializer(serializers.ModelSerializer):
    projects_count = serializers.SerializerMethodField()

    def get_projects_count(self, obj: Actor):
        projects_count = getattr(obj, 'projects_count', None)
        return projects_count or obj.get_participant_count()

    class Meta:
        model = Actor
        fields = [
            "projects_count",
            "id",
            "name",
            "alternative_names",
            "sector",
            "sector_name",
            "geo_reach",
            "belongs",
            "status_validation",
            "indigenous_group",
        ]


class ProjectBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MentionFullSerializer(serializers.ModelSerializer):
    project = ProjectBaseSerializer()
    note = NoteBasicSerializer()

    class Meta:
        model = Mention
        fields = ["project", "note"]


class ParticipantSerializer(serializers.ModelSerializer):
    mention = MentionFullSerializer()

    class Meta:
        model = Participant
        fields = ["mention", "participant_types"]


class MentionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mention
        fields = ["project", "note"]


class ParticipantMiniSerializer(ParticipantSerializer):
    mention = MentionMiniSerializer()


class OriginReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginReference
        fields = '__all__'


class ActorBaseSerializer(ActorBasicSerializer):

    parent_actor = ActorBasicSerializer()
    participants = ParticipantSerializer(many=True)
    origin_references = OriginReferenceSerializer(many=True)

    class Meta:
        model = Actor
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class ActorFullSerializer(ActorBaseSerializer):
    participants = ParticipantMiniSerializer(many=True)
    locations = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    def get_locations(self, obj: Actor):
        locations_query = Location.objects.filter(
            projects__project__mentions__participants__actor=obj
        ).distinct()
        return LocationSerializer(locations_query, many=True).data

    def get_notes(self, obj: Actor):
        return NoteBasicSerializer(
            Note.objects.filter(
                mentions__participants__actor=obj
            ).distinct(), many=True
        ).data

    def get_projects(self, obj: Actor):
        return ProjectBaseSerializer(
            Project.objects.filter(
                mentions__participants__actor=obj
            ).distinct(), many=True
        ).data


class ActorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'


class ActorEditeSerializer(ActorCreateSerializer):
    pass
