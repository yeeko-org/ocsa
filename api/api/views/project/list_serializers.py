from rest_framework import serializers

from actor.models import Actor, Participant, Interest
from impact.models import Impact
from project.models import Project, Conflict, MegaprojectType
from space_time.models import Location
from source.models import Mention
from api.views.common_serializers import BaseExportSerializer
from event.models import Event
from api.views.common_serializers import ConditionalFieldsMixin


class ActorBasicSerializer(ConditionalFieldsMixin):
    participants_count = serializers.SerializerMethodField()

    def get_participants_count(self, obj):
        return 9999

    class Meta:
        model = Actor
        # exclude = ['std_name', 'capital_id_ref']
        fields = [
            'id',
            'name',
            'participants_count',
        ]


class ActorFullSerializer(ActorBasicSerializer):

    class Meta:
        model = Actor
        fields = [
            'id',
            'name',
            'participants_count',
            'comments',
            'sector',
            'belongs',
            'status_validation',
        ]


class InterestFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = '__all__'


class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = ['id', 'interest_type', 'interest_subtype', 'participant']


class ParticipantSerializer(serializers.ModelSerializer):
    actor_full = ActorBasicSerializer(source='actor')

    class Meta:
        model = Participant
        fields = "__all__"


class ParticipantFullSerializer(serializers.ModelSerializer):
    actor_full = ActorFullSerializer(source='actor')
    interests = InterestFullSerializer(many=True)

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


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['event_type', 'date', 'description']


class MentionSerializer(serializers.ModelSerializer):
    impacts = ImpactSerializer(many=True)
    participants = ParticipantSerializer(many=True)
    events = EventSerializer(many=True)

    class Meta:
        model = Mention
        exclude = ['project']


class LocationBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['id', 'state']


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
    locations = LocationBasicSerializer(many=True, read_only=True)
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
    locations = LocationBasicSerializer(many=True, read_only=True)
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


class NoteDatesSerializer(serializers.RelatedField):

    def to_representation(self, value):
        return value.note.date.strftime("%d-%m-%Y")


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
    note_dates = NoteDatesSerializer(
        source='mentions', many=True, read_only=True)
    status_validation = serializers.ReadOnlyField(
        source='status_validation.public_name')
    status_location = serializers.ReadOnlyField(
        source='status_location.public_name')

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "alternative_name",
            "description",
            "is_grouper",
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

            "note_dates",
            "status_validation",
            "status_location",
        ]


class ConflictSerializer(ConflictSimpleSerializer):
    projects = ProjectMiniSerializer(many=True, read_only=True)


class ConflictFullSerializer(ConflictSimpleSerializer):
    projects = ProjectBasicSerializer(many=True, read_only=True)
    parent_project_full = ProjectMiniSerializer(
        read_only=True, source='parent_project')



# class ImpactExportSerializer(serializers.ModelSerializer):
#     pass
#


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

