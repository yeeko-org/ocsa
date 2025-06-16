from django.urls import include, path

from api.views.actor import ActorViewSet, ActorMiniListViewSet
from api.views.article.views import ArticleViewSet
from api.views.project import (
    ProjectViewSet, ProjectFileViewSet, ConflictViewSet, ProjectMiniViewSet)
from api.views.generic_merge.views import MergeRecordsView
from api.views.df.df_views import DisplacementViewSet
from api.views.note import NoteViewSet, NoteFileViewSet
from api.views.note.mention_views import (
    MentionViewSet, ParticipantViewSet, ImpactViewSet,
    InvolvedViewSet, InterestViewSet, StatusHistoryViewSet, EventViewSet)
from api.views.auth.login_views import UserLoginAPIView
from api.views.scraping.views import ScrapingDatesView, ScrapedRecordView
from api.views.space_time import LocationViewSet
# from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from api.views.ps_schemas.views import CollectionViewSet

router = DefaultRouter()

router.register(r'actor', ActorViewSet, basename='actor')
router.register(r'actor_mini', ActorMiniListViewSet, basename='actor mini')

router.register(r'article', ArticleViewSet, basename='article')

router.register(r'note', NoteViewSet, basename='note')
router.register(r'note_file', NoteFileViewSet, basename='note file')

router.register(r'project', ProjectViewSet, basename='project')
router.register(r'project_mini', ProjectMiniViewSet, basename='project mini')

router.register(r'conflict', ConflictViewSet, basename='conflict')
router.register(r'project_file', ProjectFileViewSet, basename='project file')

router.register(r'mention', MentionViewSet, basename='mention')
router.register(r'status_history', StatusHistoryViewSet,
                basename='status history')
router.register(r'impact', ImpactViewSet, basename='impact')
router.register(r'participant', ParticipantViewSet, basename='participant')
router.register(r'interest', InterestViewSet, basename='interest')

router.register(r'event', EventViewSet, basename='event')
router.register(r'involved', InvolvedViewSet, basename='involved')

router.register(r'displacement', DisplacementViewSet, basename='displacement')

router.register(r'location', LocationViewSet, basename='location')

router.register(r'collection', CollectionViewSet, basename='collection')

router.register(r'scraped_record', ScrapedRecordView,
                basename='scraped_record')


urlpatterns = [
    # path('login/', obtain_auth_token, name='api-login'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.views.catalogs.urls')),
    path('space_time/', include('api.views.space_time.urls')),
    path('generic_merge/', MergeRecordsView.as_view(), name='generic-merge'),
    path('scraped_date/', ScrapingDatesView.as_view(), name='generic-merge'),
    path('', include(router.urls)),
]
