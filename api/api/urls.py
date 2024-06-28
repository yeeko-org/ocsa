from django.urls import include, path

from api.views.actor import ActorViewSet, ActorMiniListViewSet
from api.views.catalogs import CatalogsView
from api.views.project import ProjectViewSet
from api.views.note import NoteViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'actors', ActorViewSet, basename='actor')
router.register(r'actors_mini', ActorMiniListViewSet, basename='actor mini')


urlpatterns = [
    path('catalogs/', include('api.views.catalogs.urls')),
    path('space_time/', include('api.views.space_time.urls')),
    path('', include(router.urls)),
]
