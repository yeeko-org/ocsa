from api.views.common_views import (
    OnlyByFilterMixin, BaseStatusViewSet, BaseGenericViewSet)
from .serializers import ArticleListSerializer, ArticleDetailSerializer
from django_filters import FilterSet
from source.models import Article


class ArticleFilter(FilterSet):

    class Meta:
        model = Article
        fields = [
            "source",
            "section",
            "is_selected",
            "scraped",
        ]


class ArticleViewSet(BaseGenericViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer
    filterset_class = ArticleFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ArticleDetailSerializer
        return super().get_serializer_class()
