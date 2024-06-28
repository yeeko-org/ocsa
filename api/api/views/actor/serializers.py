from rest_framework import serializers

from actor.models import Actor, OriginReference, Participant
from project.models import Project
from source.models import Mention, Note
from space_time.models import Location

from api.views.note.serializers import NoteBasicSerializer


class ProjectBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MentionBaseSerializer(serializers.ModelSerializer):
    project = ProjectBaseSerializer()
    note = NoteBasicSerializer()

    class Meta:
        model = Mention
        fields = ["project", "note"]


class ParticipantBaseSerializer(serializers.ModelSerializer):
    mention = MentionBaseSerializer()

    class Meta:
        model = Participant
        fields = ["mention", "participant_types"]


class MentionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mention
        fields = ["project", "note"]


class ParticipantMiniSerializer(ParticipantBaseSerializer):
    mention = MentionMiniSerializer()


class OriginReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginReference
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class ActorMiniSerializer(serializers.ModelSerializer):
    projects_count = serializers.SerializerMethodField()
    sector_group = serializers.SerializerMethodField()

    def get_projects_count(self, obj: Actor):
        projects_count = getattr(obj, 'projects_count', None)
        return projects_count or obj.get_participant_count()

    def get_sector_group(self, obj: Actor):
        sector_group = getattr(obj, "sector_group", None)
        return sector_group or obj.get_sector_group()

    class Meta:
        model = Actor
        fields = [
            "id",
            "projects_count",

            "indigenous_group",
            "sector_group",

            "name",
            "alternative_names",
            "sector",
            "sector_name",
            "geo_reach",
            "belongs",
            "status_validation",
        ]


class ActorBaseSerializer(ActorMiniSerializer):

    parent_actor = serializers.SerializerMethodField()
    participants = ParticipantBaseSerializer(many=True)

    def get_parent_actor(self, obj: Actor):
        # ActorBaseSerializer produce error de recursividad. analizar
        return ActorMiniSerializer(obj.parent_actor).data

    class Meta:
        model = Actor
        fields = '__all__'


class ActorFullSerializer(ActorBaseSerializer):
    participants = ParticipantMiniSerializer(many=True)
    notes = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    origin_references = OriginReferenceSerializer(many=True)

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
