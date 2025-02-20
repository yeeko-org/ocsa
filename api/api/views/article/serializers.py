from rest_framework import serializers
from source.models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='article-detail')

    class Meta:
        model = Article
        fields = [
            "id",
            "detail_url",
            "uid",
            "title",
            "source",
            "section",
            "url",
            "imgs",
            "basic_content",
            "scraped_date",
            "autor",
            "published_date",
            "certainty_degree",
            "is_selected",
            "scraped",
            "note",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
