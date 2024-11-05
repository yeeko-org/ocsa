from api.views.actor import ActorBaseSerializer
from api.views.common_serializers import CommonCount
from classify.models import IndigenousGroup


class IndigenousGroupSerializer(CommonCount):

    class Meta:
        model = IndigenousGroup
        fields = "__all__"


class IndigenousGroupFullSerializer(CommonCount):
    actors = ActorBaseSerializer(many=True, read_only=True)

    class Meta:
        model = IndigenousGroup
        fields = "__all__"
