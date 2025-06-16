from rest_framework import serializers

from actor.models import Actor, OriginReference, Participant
from project.models import Project
from source.models import Mention, Note
from space_time.models import Location


class ProjectBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class NoteBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ['id', 'title', 'source', 'date', 'status_register']


class MentionBaseSerializer(serializers.ModelSerializer):
    project_full = ProjectBaseSerializer(source='project', read_only=True)
    note_full = NoteBasicSerializer(source='note', read_only=True)

    class Meta:
        model = Mention
        fields = ["id", "project", "note", "project_full", "note_full"]


class ParticipantBaseSerializer(serializers.ModelSerializer):
    mention = MentionBaseSerializer()

    class Meta:
        model = Participant
        fields = ["id", "mention", "participant_types"]


class MentionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mention
        fields = ["id", "project", "note"]


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


class ActorSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = [
            "id",
            "indigenous_group",
            "name",
            "alternative_names",
            "sector",
            "geo_reach",
            "belongs",
            "status_validation",
            "network_seq",
            "children_actors",
        ]


class ActorMiniSerializer(serializers.ModelSerializer):
    mentions_count = serializers.SerializerMethodField(read_only=True)

    def get_mentions_count(self, obj: Actor):
        mentions_count = getattr(obj, 'mentions_count', None)
        return mentions_count or obj.get_participant_count()

    class Meta:
        model = Actor
        fields = [
            "id",
            "mentions_count",
            "indigenous_group",
            # "sector_group",
            "name",
            "alternative_names",
            "sector",
            "geo_reach",
            "belongs",
            "status_validation",
            "network_seq",

            "children_actors",
        ]


class ActorMiniBaseSerializer(serializers.ModelSerializer):
    parent_actor_full = serializers.SerializerMethodField(read_only=True)

    def get_parent_actor_full(self, obj: Actor):
        if obj.parent_actor:
            return ActorSimpleSerializer(obj.parent_actor).data
        return None

    class Meta:
        model = Actor
        fields = '__all__'


class ActorBaseSerializer(ActorMiniBaseSerializer):
    participants = ParticipantBaseSerializer(many=True, read_only=True)
    children_actors = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )


class ActorFullSerializer(ActorBaseSerializer):
    participants = ParticipantMiniSerializer(many=True, read_only=True)
    notes = serializers.SerializerMethodField(read_only=True)
    projects = serializers.SerializerMethodField(read_only=True)
    others_parents_full = ActorMiniSerializer(
        many=True, read_only=True, source='others_parents')
    children_actors_full = ActorMiniSerializer(
        many=True, read_only=True, source='children_actors')

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

    # def get_others_parents_full(self, obj: Actor):
    #     return ActorMiniSerializer(obj.others_parents.all(), many=True).data


class ActorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'


class ActorEditeSerializer(ActorCreateSerializer):
    pass


class ActorFullCountSerializer(ActorSimpleSerializer):
    participant_count = serializers.ReadOnlyField()
    participant_types = serializers.SerializerMethodField()

    def get_participant_types(self, obj: Actor):
        context = self.context
        project = context.get("project")
        return obj.participants.filter(
            mention__project=project
        ).values_list("participant_types", flat=True)

    # def get_mention_count(self, obj: Actor):
    #     context = self.context
    #     project = context.get("project")
    #     return Mention.objects.filter(
    #         participants__actor=obj,
    #         project=project
    #     ).count()

    class Meta:
        model = Actor
        fields = '__all__'
