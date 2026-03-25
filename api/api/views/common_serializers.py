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


class LocationExportSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    municipality = MunicipalitySerializer()
    locality = LocalitySerializer()

    class Meta:
        model = Location
        fields = '__all__'


class LocationBaseExportSerializer(serializers.ModelSerializer):
    location_id = serializers.ReadOnlyField()
    state__inegi_code = serializers.ReadOnlyField()
    state__short_name = serializers.ReadOnlyField()
    municipality__inegi_code = serializers.ReadOnlyField()
    municipality__name = serializers.ReadOnlyField()
    locality__inegi_code = serializers.ReadOnlyField()
    locality__name = serializers.ReadOnlyField()
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()


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


class InterestExportMixin:
    """Mixin for interest export serializers.

    Computes interest_subtypes, interest_types, interest_groups and
    interest texts in a single pass over obj.interests, caching the
    result on the instance to avoid re-iterating across the four
    SerializerMethodFields that consume it.
    """

    def _get_interest_data(self, obj: object) -> dict:
        """Iterate obj.interests once and cache all four lists."""
        if not hasattr(obj, '_interest_cache'):
            subtypes, types, groups, texts = [], [], [], []
            for interest in obj.interests.all():
                texts.append(interest.text)
                if interest.interest_subtype:
                    subtypes.append(interest.interest_subtype.name)
                    types.append(
                        interest.interest_subtype.interest_type.name)
                    groups.append(
                        interest.interest_subtype
                        .interest_type.interest_group.name)
                else:
                    subtypes.append(None)
                    types.append(None)
                    groups.append(None)
            obj._interest_cache = {
                'texts': texts,
                'subtypes': subtypes,
                'types': types,
                'groups': groups,
            }
        return obj._interest_cache

    def get_interests(self, obj: object) -> list:
        return self._get_interest_data(obj)['texts']

    def get_interest_subtypes(self, obj: object) -> list:
        return self._get_interest_data(obj)['subtypes']

    def get_interest_types(self, obj: object) -> list:
        return self._get_interest_data(obj)['types']

    def get_interest_groups(self, obj: object) -> list:
        return self._get_interest_data(obj)['groups']


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
