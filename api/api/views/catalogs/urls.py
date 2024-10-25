from django.urls import include, path
from api.views.catalogs import (
    ParticipantTypeViewSet,
    BelongViewSet,
    IndigenousGroupViewSet,
    SectorGroupViewSet,
    SectorViewSet,
    InterestGroupViewSet,
    InterestTypeViewSet,
    EventGroupViewSet,
    EventTypeViewSet,
    EventSubtypeViewSet,
    InvolvedRoleViewSet,
    RoleViewSet,
    SourceViewSet,
    StatusControlViewSet,
    # ExtractivismTypeViewSet,
    MegaprojectTypeViewSet
)
from api.views.catalogs.impact_views import (
    ImpactSubtypeViewSet, ImpactTypeViewSet)

from rest_framework import routers

from api.views.catalogs.all import CatalogsView

router = routers.DefaultRouter()
router.register(r'participant_type', ParticipantTypeViewSet, basename='catalog_participant_type')
router.register(r'belong', BelongViewSet, basename='catalog_belong')
router.register(r'indigenous_group', IndigenousGroupViewSet, basename='catalog_indigenous_group')
router.register(r'sector_group', SectorGroupViewSet, basename='catalog_sector_group')
router.register(r'sector', SectorViewSet, basename='catalog_sector')
router.register(r'interest_group', InterestGroupViewSet, basename='catalog_interest_group')
router.register(r'interest_type', InterestTypeViewSet, basename='catalog_interest_type')
router.register(r'event_group', EventGroupViewSet, basename='catalog_event_group')
router.register(r'event_type', EventTypeViewSet, basename='catalog_event_type')
router.register(r'event_subtype', EventSubtypeViewSet, basename='catalog_event_subtype')
router.register(r'involved_roles', InvolvedRoleViewSet, basename='catalog_event_role')
router.register(r'impact_subtype', ImpactSubtypeViewSet, basename='catalog_impact_subtype')
router.register(r'impact_type', ImpactTypeViewSet, basename='catalog_impact_type')
router.register(r'role', RoleViewSet, basename='catalog_role')
router.register(r'source', SourceViewSet, basename='catalog_source')
router.register(r'status_control', StatusControlViewSet, basename='catalog_status_control')
router.register(r'extractivism_type', MegaprojectTypeViewSet, basename='catalog_extractivism_type')
# router.register(r'megaproject_type', MegaprojectTypeViewSet, basename='catalog_megaproject_type')

urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]