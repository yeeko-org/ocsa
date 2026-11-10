from rest_framework import serializers
from event.models import Event, Involved, EventType

from api.views.actor.serializers import MentionBaseSerializer
from api.views.common_serializers import ParticipantFullSerializer
from api.permissions import BULK_ACTIONS
from project.models import Conflict
from df.models import Displacement


class InvolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Involved
        fields = '__all__'


class InvolvedFullSerializer(InvolvedSerializer):
    participant_full = ParticipantFullSerializer(
        read_only=True, source='participant')
    example = serializers.SerializerMethodField(read_only=True)

    def get_example(self, obj):
        return "SOLO"

    class Meta:
        model = Involved
        fields = '__all__'


class DisplacementSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = '__all__'


class EventMediumSerializer(serializers.ModelSerializer):
    involvements = InvolvedSerializer(many=True, read_only=True)
    displacements = DisplacementSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, attrs: dict) -> dict:
        """Sin propósito fuera de los grupos que lo usan (task-125).

        Un mecanismo legal que cambia a otro tipo conservaba su
        propósito aunque el dashboard ya no lo muestre. La edición
        masiva queda fuera a propósito: su lote no trae instancia.
        """
        attrs = super().validate(attrs)
        view = self.context.get("view")
        if getattr(view, "action", None) in BULK_ACTIONS:
            return attrs
        event_type = attrs.get("event_type") or getattr(
            self.instance, "event_type", None)
        if event_type and not event_type.event_group.show_position:
            attrs["purpose"] = None
        return attrs


class EventSerializer(EventMediumSerializer):
    involvements = InvolvedFullSerializer(many=True, read_only=True)
    mention_full = MentionBaseSerializer(read_only=True, source='mention')


class ConflictSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conflict
        fields = '__all__'
