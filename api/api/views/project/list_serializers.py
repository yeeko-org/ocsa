from rest_framework import serializers

from actor.models import Interest
from impact.models import Impact
from project.models import Project, Conflict, MegaprojectType
from space_time.models import Location
from source.models import Mention
from api.views.common_serializers import ParticipantSerializer, EventSerializer
from api.views.common_serializers import ConditionalFieldsMixin


class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = ['id', 'interest_type', 'interest_subtype', 'participant']


class ImpactSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impact
        fields = '__all__'
        read_only_fields = ['mention']


class ImpactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Impact
        fields = '__all__'


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


class MegaprojectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MegaprojectType
        fields = "__all__"


class ConflictSerializer(ConflictSimpleSerializer):
    projects = ProjectMiniSerializer(many=True, read_only=True)


class ConflictFullSerializer(ConflictSimpleSerializer):
    projects = ProjectBasicSerializer(many=True, read_only=True)
    parent_project_full = ProjectMiniSerializer(
        read_only=True, source='parent_project')


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

