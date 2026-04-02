from django.urls import include, path
from api.views.catalogs import StatusControlViewSet

from rest_framework import routers

from api.views.catalogs.all import CatalogsView
from ps_schema.registry import catalog_registry

router = routers.DefaultRouter()
router.register(r'status_control', StatusControlViewSet, basename='catalog_status_control')

# Registry-based catalogs (CatalogSchema subclasses).
# Coexists with manual registrations above during incremental migration.
# When a snake_name is migrated to the registry, remove its manual line above.
catalog_registry.register_routes(router)


urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]