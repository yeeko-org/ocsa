from rest_framework import serializers

from api.views.actor.serializers import MentionBaseSerializer
from api.views.common_serializers import LocationBaseExportSerializer
from api.views.event.serializers import ConflictSimpleSerializer

from impact.models import ImpactType, Impact


class ImpactTypeSerializer(serializers.ModelSerializer):
    impact_group  = serializers.CharField(
        source='impact_group.name', read_only=True)

    class Meta:
        model = ImpactType
        fields = "__all__"


class ImpactExportSerializer(LocationBaseExportSerializer):
    mention = MentionBaseSerializer()

    conflict = ConflictSimpleSerializer(
        source='mention.project.conflict', read_only=True)
    impact_type = ImpactTypeSerializer()
    impact_subtype = serializers.CharField(
        source='impact_subtype.name', read_only=True)

    class Meta:
        model = Impact
        fields = [
            'id',
            'description',
            'impact_type',
            'impact_subtype',

            'mention',
            'conflict',

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
        read_only_fields = fields
