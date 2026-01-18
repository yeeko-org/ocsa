
from rest_framework import serializers
from source.models import Article, ArticleQualify
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



