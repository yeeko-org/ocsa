from django.urls import include, path

from api.views.catalogs import CatalogsView
from api.views.project import ProjectViewSet
from api.views.note import NoteViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'notes', NoteViewSet, basename='note')


urlpatterns = [
    path('catalogs/', CatalogsView.as_view()),
    path('', include(router.urls)),
]
