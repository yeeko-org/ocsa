from rest_framework import serializers

from source.models import Source, ScrapedRecord


class SourceSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ["id", "name"]


class ScrapedRecordRealSimpleSerializer(serializers.ModelSerializer):
    all_counts = serializers.SerializerMethodField()

    def get_all_counts(self, obj):
        # return obj.articles\
        #     .values("certainty_degree", "second_certainty_degree", "is_selected")\
        #     .annotate(count=Count('id'))
        from django.db.models import (
            Count, Q, Case, When, IntegerField, Value, CharField, F,
            BooleanField, ExpressionWrapper)

        return obj.articles \
            .annotate(
                first_pre_selected=ExpressionWrapper(
                    Q(certainty_degree__gt=100, certainty_degree__isnull=False),
                    output_field=BooleanField()
                ),
                second_pre_selected=Case(
                    When(second_certainty_degree__gt=100, then=Value(True)),
                    When(second_certainty_degree__lte=100, then=Value(False)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                is_ready=ExpressionWrapper(
                    Q(is_selected__isnull=False),
                    output_field=BooleanField()
                )

            ) \
            .values("first_pre_selected", "second_pre_selected", "is_ready") \
            .annotate(count=Count('id'))

    class Meta:
        model = ScrapedRecord
        fields = [
            "id", "from_date", "to_date", "source", "all_counts"
        ]


class ScrapedRecordSimpleSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()
    scraped_count = serializers.SerializerMethodField()
    analyzed_count = serializers.SerializerMethodField()
    first_pre_selected_count = serializers.SerializerMethodField()
    pre_filtered_count = serializers.SerializerMethodField()
    second_pre_selected_count = serializers.SerializerMethodField()
    pending_count = serializers.SerializerMethodField()
    ready_count = serializers.SerializerMethodField()
    errors_count = serializers.SerializerMethodField()

    def get_articles_count(self, obj):
        return obj.articles.count()

    def get_scraped_count(self, obj):
        return obj.articles.filter(content__isnull=False).count()

    def get_analyzed_count(self, obj):
        return obj.articles.filter(certainty_degree__isnull=False).count()

    def get_first_pre_selected_count(self, obj):
        return obj.articles\
            .filter(certainty_degree__gt=100).count()

    def get_pre_filtered_count(self, obj):
        return obj.articles\
            .filter(second_certainty_degree__isnull=False).count()

    def get_second_pre_selected_count(self, obj):
        return obj.articles\
            .filter(second_certainty_degree__gt=100).count()

    def get_pending_count(self, obj):
        return obj.articles\
            .filter(is_selected__isnull=True)\
            .filter(second_certainty_degree__gt=100).count()

    def get_ready_count(self, obj):
        return obj.articles\
            .filter(is_selected__isnull=False)\
            .filter(second_certainty_degree__gt=100).count()

    def get_errors_count(self, obj):
        if obj.errors:
            return len(obj.errors)
        return 0

    class Meta:
        model = ScrapedRecord
        fields = [
            "id", "from_date", "to_date", "source",
            "articles_count", 'scraped_count',
            "analyzed_count", "first_pre_selected_count",
            "pre_filtered_count", "second_pre_selected_count",
            "pending_count", "ready_count", "errors_count",
            # "all_counts"
        ]


class ScrapedRecordSerializer(ScrapedRecordSimpleSerializer):
    source_full = SourceSimpleSerializer(read_only=True, source='source')

    # def get_pre_selected(self, obj):
    #     return obj.articles\
    #         .filter(certainty_degree__gt=100).count()

    class Meta:
        model = ScrapedRecord
        exclude = ["data"]


class SourceFullSerializer(serializers.ModelSerializer):
    notes_count = serializers.ReadOnlyField()
    # scraped_records = ScrapedRecordSimpleSerializer(many=True, read_only=True)

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
