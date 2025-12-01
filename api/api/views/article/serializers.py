from django.urls import reverse
from rest_framework import serializers
from source.models import Article, Source, ScrapedRecord, ArticleQualify
from api.views.note.serializers import NoteFullSerializer


class ArticleQualifySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleQualify
        fields = '__all__'


class ArticleListSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='article-detail')

    class Meta:
        model = Article
        # fields = "__all__"
        exclude = [
            'content', 'basic_content', 'metadata', 'html_content',
            'paragraphs']


class ArticleListSuperSerializer(ArticleListSerializer):
    qualifications = ArticleQualifySerializer(many=True, read_only=True)


class ArticleDetailSerializer(serializers.ModelSerializer):
    note_full = NoteFullSerializer(read_only=True, source='note')
    qualifications = ArticleQualifySerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class ArticleSuperDetailSerializer(ArticleDetailSerializer):
    qualifications = ArticleQualifySerializer(many=True, read_only=True)


class ArticleSelectedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['scraped', 'source', 'uid', 'url']


class ArticleStatusSerializer(serializers.ModelSerializer):
    note_full = NoteFullSerializer(read_only=True, source='note')
    status = serializers.SerializerMethodField()

    # def get_note_url(self, obj):
    #     request = self.context.get('request')
    #     if request and obj.note_id:
    #         return request.build_absolute_uri(
    #             reverse('note-detail', args=[obj.note_id]))

    def get_status(self, obj):
        return self.context.get('status')

    class Meta:
        model = Article
        # fields = ["status", "is_selected", "note"]
        fields = "__all__"


class ScrapedRecordSimpleSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()
    preclassified_count = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()

    def get_articles_count(self, obj):
        return obj.articles.count()

    def get_preclassified_count(self, obj):
        return obj.articles.filter(certainty_degree__isnull=False).count()

    def get_pending_count(self, obj):
        return obj.articles\
            .filter(is_selected__isnull=True)\
            .filter(certainty_degree__gt=100).count()

    class Meta:
        model = ScrapedRecord
        fields = [
            "id", "from_date", "to_date", "source", "errors",
            "articles_count", "preclassified_count", "pending_count"]


class ScrapedRecordSerializer(ScrapedRecordSimpleSerializer):
    pre_selected = serializers.SerializerMethodField()

    def get_pre_selected(self, obj):
        return obj.articles\
            .filter(certainty_degree__gt=100).count()

    class Meta:
        model = ScrapedRecord
        fields = "__all__"
        # exclude = ["articles"]


class SourceFullSerializer(serializers.ModelSerializer):
    notes_count = serializers.ReadOnlyField()
    scraped_records = ScrapedRecordSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Source
        fields = "__all__"


class ScrapingDateSerializer(serializers.Serializer):
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=False, allow_null=True)
    # source = serializers.ChoiceField(
    #     choices=['jornada', 'reforma'],
    #     required=True
    # )
    source = serializers.IntegerField(
        required=True,
        help_text="ID of the source to scrape articles from."
    )

