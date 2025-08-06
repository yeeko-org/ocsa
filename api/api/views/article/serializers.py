from django.urls import reverse
from rest_framework import serializers
from source.models import Article, Source, ScrapedRecord
from api.views.note.serializers import NoteFullSerializer


class ArticleListSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='article-detail')

    class Meta:
        model = Article
        # fields = "__all__"
        exclude = [
            'content', 'basic_content', 'metadata', 'html_content',
            'paragraphs']


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class ArticleSelectedSerializer(serializers.Serializer):
    is_selected = serializers.BooleanField()


class ArticleStatusSerializer(serializers.ModelSerializer):
    note_full = NoteFullSerializer(read_only=True, source='note')
    # note_url = serializers.SerializerMethodField()
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
    class Meta:
        model = ScrapedRecord
        fields = ["id", "from_date", "to_date", "source"]


class ScrapedRecordSerializer(serializers.ModelSerializer):
    articles_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ScrapedRecord
        fields = "__all__"


class SourceFullSerializer(serializers.ModelSerializer):
    notes_count = serializers.ReadOnlyField()
    scraped_records = ScrapedRecordSimpleSerializer(
        many=True, read_only=True)

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

