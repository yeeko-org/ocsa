from rest_framework import serializers

from api.views.catalogs.serializers import SourceSerializer
from project.models import Project
from source.models import Mention, Note


class NoteBasicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ['id', 'title', 'source', 'date', 'source']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MentionFullSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()

    class Meta:
        model = Mention
        fields = '__all__'


class NoteFullSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    mentions = MentionFullSerializer(many=True)

    class Meta:
        model = Note
        fields = '__all__'


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ['id', 'nota_id_ref', 'old_id']


class NoteEditeSerializer(NoteCreateSerializer):
    pass
