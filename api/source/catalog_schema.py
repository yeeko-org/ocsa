from ps_schema.registry import (
    catalog_registry, CatalogSchema,
    collection_registry, CollectionSchema, FilterRef, ComponentFilter,
    FilterGroupSchema,
)
from source.models import (
    Source, DiscardedReason,
    Note, NoteFile, Mention, StatusHistory, Article, ScrapedRecord,
)


@catalog_registry.register
class SourceSchema(CatalogSchema):
    model = Source
    level = "category_subtype"
    base = "status"
    permission = "admin"
    count_fields = {"notes_count": "notes"}
    filterset_fields = []
    filter_group_key = "source_types"


@catalog_registry.register
class DiscardedReasonSchema(CatalogSchema):
    model = DiscardedReason
    level = "category_subtype"
    base = "generic"
    permission = "admin"
    filter_group_key = "discarded_reasons"


@catalog_registry.register_filter_group
class ScrapedRecordFilterGroup(FilterGroupSchema):
    key_name = "scraped_record"
    name = "Bloque de scraping"
    plural_name = "Bloques de scraping"
    main_collection = "source-article"
    category_subtype = ScrapedRecord


# ---------------------------------------------------------------------------
# CollectionSchema — primary / secondary / relational
# ---------------------------------------------------------------------------

from api.views.note import NoteViewSet, NoteFileViewSet  # noqa: E402
from api.views.note.mention_views import (  # noqa: E402
    MentionViewSet, StatusHistoryViewSet)
from api.views.article.views import ArticleViewSet  # noqa: E402
from api.views.scraping.views import ScrapedRecordView  # noqa: E402


@collection_registry.register
class NoteSchema(CollectionSchema):
    model = Note
    level = "primary"
    viewset_class = NoteViewSet
    icon = "newsmode"
    color = "deep-purple"
    all_filters = [
        FilterRef("source_types"),
        ComponentFilter(title="Fechas", component="RangeDates", field="date"),
        ComponentFilter(
            title="Editor", field="editor",
            component="UserSelect", hidden=True),
        ComponentFilter(
            title="Revisor", field="reviewer",
            component="UserSelect", hidden=True),
        ComponentFilter(
            title="Con archivos", field="has_files",
            component="TripleBooleanFilter", hidden=True),
    ]


@collection_registry.register
class MentionSchema(CollectionSchema):
    model = Mention
    level = "relational"
    viewset_class = MentionViewSet


@collection_registry.register
class StatusHistorySchema(CollectionSchema):
    model = StatusHistory
    level = "secondary"
    viewset_class = StatusHistoryViewSet
    name = "Cambio al status"
    icon = "history_toggle_off"


@collection_registry.register
class NoteFileSchema(CollectionSchema):
    model = NoteFile
    level = "relational"
    viewset_class = NoteFileViewSet


@collection_registry.register
class ArticleSchema(CollectionSchema):
    model = Article
    level = "primary"
    viewset_class = ArticleViewSet
    name = "Pre-Notas"
    plural_name = "Pre-Notas"
    icon = "newspaper"
    color = "deep-purple"
    cat_params = {"init_display": True}
    all_filters = [
        FilterRef("source_types"),
        FilterRef("discarded_reasons", hidden=True),
        ComponentFilter(
            title="Fechas", component="RangeDates", field="published_date"),
        ComponentFilter(
            title="Status", field="status",
            component="OnlyByFilter",
            custom_options=[
                {"plural_name": "Faltan validar", "value": "to_validate"},
                {"plural_name": "Validados", "value": "validated"},
                {"plural_name": "Rechazados", "value": "rejected"},
                {"plural_name": "Poco probables", "value": "unlikely"},
                {"plural_name": "Reincluidos", "value": "reincluded"},
                {"plural_name": "Descartados", "value": "discarded"},
            ]),
    ]


@collection_registry.register
class ScrapedRecordSchema(CollectionSchema):
    model = ScrapedRecord
    level = "relational"
    viewset_class = ScrapedRecordView
    name = "Bloque de scraping"
    plural_name = "Bloques de scraping"
    all_filters = [
        FilterRef("source_types"),
    ]