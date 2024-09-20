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
    EventRoleViewSet,
    ImpactSubtypeViewSet,
    ImpactTypeViewSet,
    RoleViewSet,
    SourceViewSet,
    StatusControlViewSet,
    MegaprojectTypeViewSet
)

from rest_framework import routers

from api.views.catalogs.all import CatalogsView

router = routers.DefaultRouter()
router.register(r'participant_types', ParticipantTypeViewSet, basename='catalog_participant_type')
router.register(r'belongs', BelongViewSet, basename='catalog_belong')
router.register(r'indigenous_groups', IndigenousGroupViewSet, basename='catalog_indigenous_group')
router.register(r'sector_groups', SectorGroupViewSet, basename='catalog_sector_group')
router.register(r'sectors', SectorViewSet, basename='catalog_sector')
router.register(r'interest_groups', InterestGroupViewSet, basename='catalog_interest_group')
router.register(r'interest_types', InterestTypeViewSet, basename='catalog_interest_type')
router.register(r'event_groups', EventGroupViewSet, basename='catalog_event_group')
router.register(r'event_types', EventTypeViewSet, basename='catalog_event_type')
router.register(r'event_subtypes', EventSubtypeViewSet, basename='catalog_event_subtype')
router.register(r'event_roles', EventRoleViewSet, basename='catalog_event_role')
router.register(r'impact_subtypes', ImpactSubtypeViewSet, basename='catalog_impact_subtype')
router.register(r'impact_types', ImpactTypeViewSet, basename='catalog_impact_type')
router.register(r'roles', RoleViewSet, basename='catalog_role')
router.register(r'sources', SourceViewSet, basename='catalog_source')
router.register(r'status_controls', StatusControlViewSet, basename='catalog_status_control')
router.register(r'megaproject_types', MegaprojectTypeViewSet, basename='catalog_megaproject_type')

urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]