from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.space_time import (
    CountryListViewSet,
    StateListViewSet,
    MunicipalityListViewSet,
    LocalityListViewSet,
    LocationListViewSet,
)

router = DefaultRouter()

router.register(
    r'countries', CountryListViewSet, basename='space_time_country')
router.register(
    r'states', StateListViewSet, basename='space_time_state')
router.register(
    r'municipalities', MunicipalityListViewSet, basename='space_time_municipality')
router.register(
    r'localities', LocalityListViewSet, basename='space_time_locality')
router.register(
    r'locations', LocationListViewSet, basename='space_time_location')
urlpatterns = [
    path('', include(router.urls)),
]
