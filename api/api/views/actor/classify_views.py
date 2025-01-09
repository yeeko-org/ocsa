from actor.models import Actor
from api.views.actor.classify_serializers import IndigenousGroupSerializer, IndigenousGroupFullSerializer
from api.views.common_views import BaseViewSet, BaseStatusViewSet
from classify.models import IndigenousGroup


class IndigenousGroupViewSet(BaseStatusViewSet):
    from django.db.models import Count
    queryset = IndigenousGroup.objects.all()\
        .annotate(count=Count('actors'))\
        .distinct()

    serializer_class = IndigenousGroupSerializer

    def get_from_obj(self, from_id):
        return IndigenousGroup.objects.get(id=from_id)

    def update_relations_merge(self, from_obj, to_obj):
        Actor.objects.filter(indigenous_group=from_obj)\
            .update(indigenous_group=to_obj)

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': IndigenousGroupFullSerializer,
            # 'retrieve': IndigenousGroupSerializer,
            'create': IndigenousGroupSerializer,
            'update': IndigenousGroupSerializer
        }
        return action_serializer.get(self.action, self.serializer_class)
