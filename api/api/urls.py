from django.urls import include, path

from api.views.actor import ActorViewSet, ActorMiniListViewSet
from api.views.project import ProjectViewSet, ProjectFileViewSet
from api.views.note import NoteViewSet, NoteFileViewSet
from api.views.note.mention_views import (
    MentionViewSet, ParticipantViewSet, ImpactViewSet,
    InvolvedViewSet, InterestViewSet, StatusHistoryViewSet)
from api.views.event import EventViewSet
from api.views.auth.login_views import UserLoginAPIView
from api.views.space_time import LocationViewSet
# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'actor', ActorViewSet, basename='actor')
router.register(r'actor_mini', ActorMiniListViewSet, basename='actor mini')

router.register(r'note', NoteViewSet, basename='note')
router.register(r'note_file', NoteFileViewSet, basename='note file')

router.register(r'project', ProjectViewSet, basename='project')
router.register(r'project_file', ProjectFileViewSet, basename='project file')

router.register(r'mention', MentionViewSet, basename='mention')
router.register(r'status_history', StatusHistoryViewSet, basename='status history')
router.register(r'impact', ImpactViewSet, basename='impact')
router.register(r'participant', ParticipantViewSet, basename='participant')
router.register(r'interest', InterestViewSet, basename='interest')
router.register(r'event', EventViewSet, basename='event')
router.register(r'involved', InvolvedViewSet, basename='involved')

router.register(r'location', LocationViewSet, basename='location')


urlpatterns = [
    # path('login/', obtain_auth_token, name='api-login'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.views.catalogs.urls')),
    path('space_time/', include('api.views.space_time.urls')),
    path('', include(router.urls)),
]
