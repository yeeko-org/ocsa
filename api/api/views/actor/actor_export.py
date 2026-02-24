from rest_framework import serializers
from actor.models import Actor
from api.views.common_serializers import NoteDatesActorSerializer


xlsx_actor_fields = [
    {
        "special_group": "actor",
    },
    {
        "name": "Número de notas",
        "width": 15,
        "field": "note_dates",
        "operation": "count"
    },
    {
        "name": "Primera nota",
        "width": 15,
        "field": "note_dates",
        "operation": "min"
    },
    {
        "name": "Status de validación",
        "width": 15,
        "field": "status_validation",
        "conditions": ["only_logged_in"]
    },
    {
        "name": "Última nota",
        "width": 15,
        "field": "note_dates",
        "operation": "max"
    }
]


class ActorSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = [
            "id",
            "name",
        ]

class BelongsRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return ", ".join(value.values_list('name', flat=True))


class CountriesRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return ", ".join(value.values_list('name', flat=True))


class ActorExportSerializer(serializers.ModelSerializer):
    sector = serializers.CharField(source='sector.name', read_only=True)
    sector_group = serializers.CharField(
        source='sector.sector_group.name', read_only=True)
    belongs = BelongsRepSerializer(read_only=True)
    indigenous_group = serializers.CharField(
        source='indigenous_group.name', read_only=True)
    countries = CountriesRepSerializer(read_only=True)

    class Meta:
        model = Actor
        fields = [
            "id",
            "name",
            "alternative_names",
            "sex",

            "sector",
            "sector_group",
            "belongs",
            "indigenous_group",
            "countries",
        ]


class ActorFullExportSerializer(ActorExportSerializer):
    parent_actor = ActorSimpleSerializer()
    note_dates = NoteDatesActorSerializer(
        source='participants', many=True, read_only=True)
    status_validation = serializers.CharField(
        source='status_validation.public_name', read_only=True)

    class Meta:
        model = Actor
        fields = [
            "id",
            "name",
            "alternative_names",
            "sex",

            "parent_actor",
            "sector",
            "sector_group",
            "belongs",
            "indigenous_group",
            "countries",

            "note_dates",
            "status_validation",
        ]

