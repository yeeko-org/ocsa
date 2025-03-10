from django.urls import reverse
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


class ArticleSelectedSerializer(serializers.Serializer):
    is_selected = serializers.BooleanField()


class ArticleStatusSerializer(serializers.ModelSerializer):
    note_url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_note_url(self, obj):
        request = self.context.get('request')
        if request and obj.note_id:
            return request.build_absolute_uri(
                reverse('note-detail', args=[obj.note_id]))

    def get_status(self, _):
        return self.context.get('status')

    class Meta:
        model = Article
        fields = ["status", "is_selected", "note", "note_url"]
