from rest_framework import serializers

from source.models import ScrapedRecord


class ScrapingDateSerializer(serializers.Serializer):
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=False, allow_null=True)
    source = serializers.ChoiceField(
        choices=['jornada', 'reforma'],
        required=True
    )


class ScrapedRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScrapedRecord
        fields = "__all__"
