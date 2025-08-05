from django.urls import include, path
from api.views.catalogs import (
    InterestGroupViewSet,
    InterestTypeViewSet,
    InterestSubtypeViewSet,
    InvolvedRoleViewSet,
    StatusControlViewSet,
    StatusProjectViewSet,
    ExtractivismTypeViewSet,
    MegaprojectTypeViewSet
)
from api.views.article.views import SourceViewSet
from api.views.catalogs.event_views import (
    EventGroupViewSet, EventTypeViewSet, EventSubtypeViewSet,
    PurposeViewSet)
from api.views.actor.classify_views import IndigenousGroupViewSet, SectorViewSet, SectorGroupViewSet, \
    ParticipantGroupViewSet, ParticipantTypeViewSet, BelongViewSet, CountryViewSet
from api.views.catalogs.impact_views import (
    ImpactSubtypeViewSet, ImpactTypeViewSet, ImpactGroupViewSet)
from api.views.df.df_views import (
    DimensionViewSet, PopulationSizeViewSet, TemporalityViewSet)

from rest_framework import routers

from api.views.catalogs.all import CatalogsView

router = routers.DefaultRouter()
router.register(r'participant_group', ParticipantGroupViewSet, basename='catalog_participant_group')
router.register(r'participant_type', ParticipantTypeViewSet, basename='catalog_participant_type')
router.register(r'belong', BelongViewSet, basename='catalog_belong')
router.register(r'indigenous_group', IndigenousGroupViewSet, basename='catalog_indigenous_group')
router.register(r'sector_group', SectorGroupViewSet, basename='catalog_sector_group')
router.register(r'sector', SectorViewSet, basename='catalog_sector')
router.register(r'country', CountryViewSet, basename='catalog_country')

router.register(r'interest_group', InterestGroupViewSet, basename='catalog_interest_group')
router.register(r'interest_type', InterestTypeViewSet, basename='catalog_interest_type')
router.register(r'interest_subtype', InterestSubtypeViewSet, basename='catalog_interest_subtype')

router.register(r'event_group', EventGroupViewSet, basename='catalog_event_group')
router.register(r'event_type', EventTypeViewSet, basename='catalog_event_type')
router.register(r'event_subtype', EventSubtypeViewSet, basename='catalog_event_subtype')
router.register(r'purpose', PurposeViewSet, basename='catalog_purpose')
router.register(r'involved_role', InvolvedRoleViewSet, basename='catalog_involved_role')

router.register(r'dimension', DimensionViewSet, basename='catalog_dimension')
router.register(r'population_size', PopulationSizeViewSet, basename='catalog_population_size')
router.register(r'temporality', TemporalityViewSet, basename='catalog_temporality')

router.register(r'extractivism_type', ExtractivismTypeViewSet, basename='catalog_extractivism_type')
router.register(r'megaproject_type', MegaprojectTypeViewSet, basename='catalog_megaproject_type')
router.register(r'status_project', StatusProjectViewSet, basename='catalog_status_project')
# router.register(r'megaproject_type', MegaprojectTypeViewSet, basename='catalog_megaproject_type')

router.register(r'impact_group', ImpactGroupViewSet, basename='catalog_impact_group')
router.register(r'impact_type', ImpactTypeViewSet, basename='catalog_impact_type')
router.register(r'impact_subtype', ImpactSubtypeViewSet, basename='catalog_impact_subtype')

router.register(r'source', SourceViewSet, basename='catalog_source')
router.register(r'status_control', StatusControlViewSet, basename='catalog_status_control')


urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]