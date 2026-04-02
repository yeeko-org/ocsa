from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.space_time import (
    StateListViewSet,
    MunicipalityListViewSet,
)

router = DefaultRouter()

router.register(r'state', StateListViewSet, basename='space_time_state')
router.register(
    r'municipality', MunicipalityListViewSet, basename='space_time_municipality')

urlpatterns = [
    path('', include(router.urls)),
]
