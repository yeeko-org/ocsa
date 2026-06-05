from django.urls import include, path

from api.views.map.views import (
    ProjectMapViewSet, ProjectLocationViewSet, NoteMapViewSet)
from api.views.map.index_views import (
    ProjectFacetsView, MapActorsView, RebuildMapIndexView)
from api.views.generic_merge.views import MergeRecordsView
from api.views.auth.login_views import UserLoginAPIView
from api.views.scraping.views import ScrapingDatesView
from api.views.task import ActivityView, OfflineTaskViewSet
# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from api.views.ps_schemas.views import CollectionViewSet
from ps_schema.registry import collection_registry

router = DefaultRouter()

router.register(r'project_map', ProjectMapViewSet, basename='project map')

router.register(r'note_map', NoteMapViewSet, basename='note_map')

router.register(r'project_location', ProjectLocationViewSet,
                basename='project_location')

router.register(r'collection', CollectionViewSet, basename='collection')

router.register(r'offline_task', OfflineTaskViewSet)

collection_registry.register_routes(router)


urlpatterns = [
    # path('login/', obtain_auth_token, name='api-login'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('activity/', ActivityView.as_view(), name='activity'),
    path('catalogs/', include('api.views.catalogs.urls')),
    path('space_time/', include('api.views.space_time.urls')),
    path('map/project_facets/', ProjectFacetsView.as_view(),
         name='map-project-facets'),
    path('map/actors/', MapActorsView.as_view(), name='map-actors'),
    path('map/index/rebuild/', RebuildMapIndexView.as_view(),
         name='map-index-rebuild'),
    path('generic_merge/', MergeRecordsView.as_view(), name='generic-merge'),
    path('scraped_date/', ScrapingDatesView.as_view(), name='scraping-dates'),
    path('', include(router.urls)),
]
