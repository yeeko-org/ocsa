from rest_framework import serializers

from actor.models import Actor, Participant, Interest
from event.models import Event
from project.models import Conflict
from space_time.models import Location, State, Municipality, Locality


class CommonCount(serializers.ModelSerializer):
    count = serializers.ReadOnlyField()


class ConditionalFieldsMixin(serializers.ModelSerializer):
    """
    A serializer mixin that conditionally excludes fields based on
    user authentication.
    """

    def to_representation(self, instance):
        """
        Override to_representation to handle conditional fields.
        """
        data = super().to_representation(instance)
        context = self.context
        protected_fields = [
            'status_register', 'comments', 'status_validation',
            'status_location']

        request = context.get('request')
        is_authenticated = request and request.user.is_authenticated
        if not is_authenticated:
            for field in protected_fields:
                if field in data:
                    data.pop(field)
        return data


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ['id', 'name', 'inegi_code']


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ['id', 'name', 'inegi_code']



class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = ['id', 'name', 'inegi_code']


class MunicipalitySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ["id", "name", "state"]


class LocalitySimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Locality
        fields = ["id", "name", "municipality"]


class NoteDatesSerializer(serializers.RelatedField):

    def to_representation(self, value):
        return value.note.date.strftime("%d-%m-%Y")


class NoteDatesActorSerializer(serializers.RelatedField):

    def to_representation(self, value):
        return value.mention.note.date.strftime("%d-%m-%Y")


class GenericNameRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.name


class GenericTextRepSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.text


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


class ParticipantSerializer(serializers.ModelSerializer):
    actor_full = ActorBasicSerializer(source='actor', read_only=True)

    class Meta:
        model = Participant
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'event_type', 'description', 'purpose']


class InterestFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = '__all__'


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


class ParticipantFullSerializer(serializers.ModelSerializer):
    actor_full = ActorFullSerializer(read_only=True, source='actor')
    interests = InterestFullSerializer(many=True, read_only=True)
    class Meta:
        model = Participant
        fields = '__all__'


class ParticipantInterestFullSerializer(ParticipantSerializer):
    interests = InterestFullSerializer(many=True, read_only=True)


class ConflictSerializer(ConditionalFieldsMixin):
    class Meta:
        model = Conflict
        fields = '__all__'
