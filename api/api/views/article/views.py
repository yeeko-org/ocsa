from django.conf import settings

from django_filters import FilterSet, NumberFilter, DateFilter, CharFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from source.models import Article, Note, NoteFile

from api.views.common_views import (
    BaseGenericViewSet, ClickHistoryMixin)
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer,
    ArticleSuperDetailSerializer, ArticleListSuperSerializer,
    ArticleSelectedSerializer, ArticleStatusSerializer)


class ArticleFilter(FilterSet):
    scraped_record = NumberFilter(
        field_name="scraped__id", lookup_expr="exact")
    status = CharFilter(method='custom_filter_status')
    status_retro = CharFilter(field_name='status_retro__name')

    # { "plural_name": "Validados", "value": "validated" },
    # { "plural_name": "Rechazados", "value": "rejected" },
    # { "plural_name": "Requiere validar", "value": "to_validate" },
    # { "plural_name": "Poco probables", "value": "unlikely" },
    # { "plural_name": "Descartados", "value": "discarded" },

    def custom_filter_status(self, queryset, name, value):
        from django.db.models import Q
        # print(f"Name: {name}, Value: {value}")
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
            'published_date': ['gte', 'lte'],
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
        from source.criteria.pre_capture import PreCaptureManager
        article = self.get_object()
        context = self.get_serializer_context()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

        manager = PreCaptureManager(user=request.user)
        manager.build_direct_criteria(article)

        context["status"] = "selected"
        return Response(
            ArticleStatusSerializer(article, context=context).data)


