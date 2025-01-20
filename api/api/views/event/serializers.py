from rest_framework import serializers
from event.models import Event, Involved

from api.views.actor.serializers import MentionBaseSerializer


class InvolvedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Involved
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    involvements = InvolvedSerializer(many=True)
    mention_full = MentionBaseSerializer(read_only=True, source='mention')

    class Meta:
        model = Event
        fields = '__all__'


class EventFullSerializer(serializers.ModelSerializer):
    involvements = InvolvedSerializer(many=True)
    mention = MentionBaseSerializer()

    class Meta:
        model = Event
        fields = '__all__'



