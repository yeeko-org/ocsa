import requests
from django.db.models import Count
from django.conf import settings

from django_filters import FilterSet, NumberFilter, DateFilter, CharFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from source.models import Article, Note, NoteFile, Source, DiscardedReason

from api.views.common_views import (
    BaseGenericViewSet, BaseStatusViewSet, ClickHistoryMixin)
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    ArticleSuperDetailSerializer, ArticleListSuperSerializer,
    ArticleSelectedSerializer, ArticleStatusSerializer)
from .source_serializers import SourceFullSerializer
from api.views.catalogs.serializers import (
    SourceSerializer, DiscardedReasonSerializer)
from ...permissions import IsAdminOrReadOnly


class ArticleFilter(FilterSet):
    scraped_record = NumberFilter(
        field_name="scraped__id", lookup_expr="exact")
    start_date = DateFilter(field_name='published_date', lookup_expr='gte')
    end_date = DateFilter(field_name='published_date', lookup_expr='lte')
    status = CharFilter(method='custom_filter_status')
    status_retro = CharFilter(field_name='status_retro__name')

    # { "plural_name": "Validados", "value": "validated" },
    # { "plural_name": "Rechazados", "value": "rejected" },
    # { "plural_name": "Requiere validar", "value": "to_validate" },
    # { "plural_name": "Poco probables", "value": "unlikely" },
    # { "plural_name": "Descartados", "value": "discarded" },

    def custom_filter_status(self, queryset, name, value):
        from django.db.models import Q
        print(f"Name: {name}, Value: {value}")
        if not value:
            return queryset

        if value == "validated":
            return queryset.filter(is_selected=True)

        if value in ["rejected", "to_validate"]:
            queryset = queryset.filter(certainty_degree__gt=100)
            queryset = queryset.filter(
                Q(second_certainty_degree__isnull=True) |
                Q(second_certainty_degree__gt=100))
        elif value in ["unlikely", "discarded", "reincluded"]:
            queryset = queryset.filter(certainty_degree__lte=100)\
                .filter(
                    Q(second_certainty_degree__isnull=True) |
                    Q(second_certainty_degree__lte=100))

        if value in ["rejected", "discarded"]:
            queryset = queryset.filter(is_selected=False)
        elif value == "reincluded":
            queryset = queryset.filter(is_selected=True)
        elif value in ["to_validate", "unlikely"]:
            queryset = queryset.filter(is_selected__isnull=True)

        return queryset

    class Meta:
        model = Article
        fields = {
            "source": ["exact"],
            "discarded_reason": ["exact"],
            "is_selected": ["exact"],
        }


class ArticleViewSet(ClickHistoryMixin, BaseGenericViewSet):
    queryset = Article.objects\
        .exclude(certainty_degree__isnull=True)
    # .exclude(certainty_degree=0)\
    serializer_class = ArticleListSerializer
    filterset_class = ArticleFilter
    search_fields = ["title", "subtitle", "author"]
    click_actions = ["opened"]
    show_tests = getattr(settings, "SHOW_TEST_PROMPTS", False)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.show_tests:
            return queryset.prefetch_related('qualifications')
        return queryset\

    def get_serializer_class(self):
        if self.action == "retrieve":
            if self.show_tests:
                return ArticleSuperDetailSerializer
            return ArticleDetailSerializer
        elif self.action == "select":
            return ArticleSelectedSerializer
        elif self.show_tests:
            return ArticleListSuperSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["patch"])
    def select(self, request, pk=None):
        article = self.get_object()
        context = self.get_serializer_context()

        # print("article", article.id)
        # request.data["id"] = pk
        # print("request.data", request.data)
        serializer = self.get_serializer(data=request.data)
        # print("name of serializer:", serializer.__class__.__name__)
        serializer.is_valid(raise_exception=True)
        # print("serializer.validated_data", serializer.validated_data)
        # article.is_selected = serializer.validated_data["is_selected"]
        # article.discarded_reason = serializer.validated_data.get(
        #     "discarded_reason", None)
        # if other_reason := serializer.validated_data.get(
        #         "other_discarded_reason"):
        #     article.other_discarded_reason = other_reason

        serializer.update(article, serializer.validated_data)


        self.save_click_action(request, article, force=True)

        if not article.is_selected:
            context["status"] = "unselected"
            return Response(
                ArticleStatusSerializer(article, context=context).data)

        exist_note = article.note
        if not exist_note:
            exist_note = Note.objects\
                .filter(source=article.source, link=article.url)\
                .first()
            if exist_note:
                article.note = exist_note
                article.save()

        if exist_note:
            context["status"] = "note_exists"
            return Response(
                ArticleStatusSerializer(article, context=context).data)

        try:
            # for reforma
            pages = article.get_meta("pagina").get("texto")
        except:
            pages = None

        note = Note.objects.create(
            title=article.title,
            subtitle=article.subtitle,
            author=article.author,
            source=article.source,
            section=article.section,
            pages=pages,
            link=article.url,
            date=article.published_date,
            status_register_id="ia_selected",
        )

        file_url = get_url_file_reforma(article)

        if file_url:
            note_file = NoteFile()
            note_file.note = note
            note_file.save_file_from_url(file_url, f"{pages}.pdf")
            note_file.save()

        article.note = note
        article.save()
        context["status"] = "selected"
        return Response(
            ArticleStatusSerializer(article, context=context).data)


def get_url_file_reforma(article: Article):
    try:
        pages = (article.get_meta("pagina") or {}).get("texto")
    except:
        return

    if not pages or not article.published_date:
        return

    published_str = article.published_date.strftime("%Y%m%d")
    reforma_url = f"https://hemeroteca.reforma.com/{published_str}/pdfs/{pages}.PDF"

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",

    }

    response = requests.post(
        "https://www.reforma.com/edicionimpresa/aplicacionei/webview/GeneraUrl.aspx/PathCDN",
        json={"Url": reforma_url}, headers=headers
    )
    if response.status_code == 200:
        try:
            return response.json().get("d")
        except:
            pass


class SourceViewSet(BaseStatusViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = []
    queryset = Source.objects.all()\
        .annotate(notes_count=Count('notes'))\
        .distinct()
    serializer_class = SourceSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': SourceFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "get":
            return queryset \
                .prefetch_related('scraped_records',
                                  'scraped_records__articles')
        return queryset

class DiscardedReasonViewSet(BaseGenericViewSet):
    queryset = DiscardedReason.objects.all()
    serializer_class = DiscardedReasonSerializer
    permission_classes = [IsAdminOrReadOnly]
