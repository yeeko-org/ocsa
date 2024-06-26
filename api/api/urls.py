from django.urls import include, path

from api.views.catalogs import CatalogsView
from api.views.project import ProjectViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')


urlpatterns = [
    path('catalogs/', CatalogsView.as_view()),
    path('', include(router.urls)),
]
