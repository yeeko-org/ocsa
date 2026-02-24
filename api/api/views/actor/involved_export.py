from rest_framework import serializers
from event.models import Involved
from api.views.actor.serializers import MentionBaseSerializer
from api.views.common_serializers import (
    GenericTextRepSerializer, GenericNameRepSerializer)
from api.views.actor.actor_export import ActorExportSerializer
from api.views.event.serializers import EventExportSerializer


xlsx_participant_fields = [
    {
        "name": "ID de la participación del actor en un evento",
        "width": 5,
        "field": "id"
    },
    {
        "special_group": "actor",
        "preset": "actor",
    },
    {
        "name": "Posición en el evento",
        "width": 15,
        "field": "participant_groups",
    },
    {
        "name": "Cómo participó el actor en el evento",
        "width": 15,
        "field": "participant_types",
    },
    {
        "name": "Rol respecto al proyecto",
        "width": 15,
        "field": "involved_role",
    },
    # {
    #     "special_group": "event",
    #     "preset": "event",
    # },
    {
        "name": "Grupo de interés del actor",
        "width": 35,
        "field": "interest_types",
        "conditions": ["only_logged_in"]
    },
    {
        "name": "Tipo de interés del actor",
        "width": 35,
        "field": "interest_groups",
        "conditions": ["only_logged_in"]
    },
    {
        "name": "Subtipo de interés del actor",
        "width": 35,
        "field": "interests__interest_subtype",
        "conditions": ["only_logged_in"]
    },
    {
        "name": "Descripción del interés del actor",
        "width": 35,
        "field": "interests",
    },
    {
        "special_group": "mention"
    },
]

class BelongsRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return ", ".join(value.values_list('name', flat=True))


class ParticipantGroupRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.participant_group.name


class InterestSubtypeRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if not value.interest_subtype:
            return None
        return value.interest_subtype.name


class InterestTypeRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if not value.interest_subtype:
            return None
        return value.interest_subtype.interest_type.name


class InterestGroupRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if not value.interest_subtype:
            return None
        return value.interest_subtype.interest_type.interest_group.name


class EventInvolvedRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.event


class InvolvementsRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.id


class InvolvedExportSerializer(serializers.ModelSerializer):
    actor = ActorExportSerializer()
    # participant_groups = InvolvedGroupRepSerializer(
    #     source='participant_types', many=True, read_only=True)
    # participant_types = GenericNameRepSerializer(
    #     many=True, read_only=True)
    involved_role = serializers.CharField(
        source='involved_role.name', read_only=True)
    event = EventExportSerializer(read_only=True)
    mention = MentionBaseSerializer(source='event.mention')

    class Meta:
        model = Involved
        fields = [
            "id",
            "actor",
            # "participant_groups",
            # "participant_types",
            "involved_role",
            "event",
            "mention",
        ]


class InvolvedExportLoggedSerializer(InvolvedExportSerializer):
    interest_subtypes = InterestSubtypeRepSerializer(
        source='interests', read_only=True, many=True)
    interest_types = InterestTypeRepSerializer(
        source='interests', read_only=True, many=True)
    interest_groups = InterestGroupRepSerializer(
        source='interests', read_only=True, many=True)

    class Meta:
        model = Involved
        fields = [
            "id",
            "actor",

            # "participant_groups",
            # "participant_types",
            "involved_role",
            # "event",
            "mention",
        ]

