from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from ps_schema.models import Level, Collection, FilterGroup
from ps_schema import generate_serializer
from ps_schema.registry import catalog_registry
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
        # print("networks", networks)
        network_list_sorted = sorted(list(networks))
        final_networks = [{"name": f"Red {i}", "id": i}
                          for i in network_list_sorted]
        catalogs = {
            "user": [],
            "offline_types": { k: v for k, v in OFFLINE_TYPES },
            "network": final_networks,
        }
        catalogs.update(catalog_registry.get_catalog_dump())
        manual_registry = {
            "qualify_schema": QualifySchema,
            "levels": Level,
            "collections": Collection,
            "filter_groups": FilterGroup,
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
