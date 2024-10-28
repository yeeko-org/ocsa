from django.urls import include, path

from api.views.actor import ActorViewSet, ActorMiniListViewSet
from api.views.project import ProjectViewSet, ProjectFileViewSet
from api.views.note import NoteViewSet, NoteFileViewSet
from api.views.event import EventViewSet

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'project', ProjectViewSet, basename='project')
router.register(r'project_file', ProjectFileViewSet, basename='project file')
router.register(r'note', NoteViewSet, basename='note')
router.register(r'note_file', NoteFileViewSet, basename='note file')
router.register(r'actor', ActorViewSet, basename='actor')
router.register(r'actor_mini', ActorMiniListViewSet, basename='actor mini')
router.register(r'event', EventViewSet, basename='event')


urlpatterns = [
    path('login/', obtain_auth_token, name='api-login'),
    path('catalogs/', include('api.views.catalogs.urls')),
    path('space_time/', include('api.views.space_time.urls')),
    path('', include(router.urls)),
]
