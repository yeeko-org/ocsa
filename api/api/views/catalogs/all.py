from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ps_schema import generate_serializer
from ps_schema.models import LEVEL_CHOICES
from ps_schema.registry import catalog_registry, collection_registry
from source.models import QualifySchema
from work_flux.models import StatusControl

from profile_auth.models import User
from api.views.auth.serializers import UserProfileSerializer

from actor.models import Actor


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        from task.models import OFFLINE_TYPES
        networks = Actor.objects\
            .filter(network_seq__isnull=False)\
            .values_list('network_seq', flat=True)\
            .distinct()
        network_list_sorted = sorted(list(networks))
        final_networks = [{"name": f"Red {i}", "id": i}
                          for i in network_list_sorted]
        catalogs = {
            "user": [],
            "offline_types": {k: v for k, v in OFFLINE_TYPES},
            "network": final_networks,
            "levels": [{"key_name": k, "name": v} for k, v in LEVEL_CHOICES],
            "collections": (
                collection_registry.get_collections_data() +
                catalog_registry.get_collections_data()
            ),
            "filter_groups": list(catalog_registry.iter_filter_group_data()),
        }
        catalogs.update(catalog_registry.get_catalog_dump())
        manual_registry = {
            "qualify_schema": QualifySchema,
            "status_control": StatusControl,
        }
        for key, model_cls in manual_registry.items():
            ser_class = generate_serializer(model_cls)
            catalogs[key] = ser_class(
                model_cls.objects.all(), many=True).data
        if self.request.user.is_authenticated:
            all_users = User.objects.all() \
                .order_by('-full_editor', '-is_staff', 'is_superuser', 'email')
            catalogs["user"] = UserProfileSerializer(
                all_users, many=True).data
        return Response(catalogs)
