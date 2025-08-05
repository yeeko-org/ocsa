import requests
from django.db.models import Count

from django_filters import FilterSet, NumberFilter, DateFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from source.models import Article, Note, NoteFile, Source

from api.views.common_views import BaseGenericViewSet, BaseStatusViewSet
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    ArticleSelectedSerializer, ArticleStatusSerializer, SourceFullSerializer)
from ..catalogs import SourceSerializer
from ...permissions import IsAdminOrReadOnly


class ArticleFilter(FilterSet):
    scraped_record = NumberFilter(
        field_name="scraped__id", lookup_expr="exact")
    start_date = DateFilter(field_name='scraped_date', lookup_expr='gte')
    end_date = DateFilter(field_name='scraped_date', lookup_expr='lte')

    class Meta:
        model = Article
        fields = {
            "source": ["exact"],
            "is_selected": ["exact"],
        }


class ArticleViewSet(BaseGenericViewSet):
    queryset = Article.objects\
        .exclude(certainty_degree=0)\
        .exclude(certainty_degree__isnull=True)
    serializer_class = ArticleListSerializer
    filterset_class = ArticleFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ArticleDetailSerializer
        elif self.action == "select":
            return ArticleSelectedSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["post"])
    def select(self, request, pk=None):
        article = self.get_object()
        context = self.get_serializer_context()

        if article.note:
            context["status"] = "note_exists"
            return Response(
                ArticleStatusSerializer(article, context=context).data)

        if article.is_selected != None:
            context["status"] = "already_selected"
            return Response(
                ArticleStatusSerializer(article, context=context).data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article.is_selected = serializer.validated_data["is_selected"]
        article.save()

        if not article.is_selected:
            context["status"] = "unselected"
            return Response(
                ArticleStatusSerializer(article, context=context).data)

        exist_note = Note.objects.filter(
            source=article.source, link=article.url
        ).first()

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
            author=article.autor,
            source=article.source,
            section=article.section,
            pages=pages,
            link=article.url,
            date=article.published_date,
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
