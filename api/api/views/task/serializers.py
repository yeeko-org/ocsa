from rest_framework import serializers

from task.models import ClickHistory, OfflineTask
from source.models import ScrapedRecord
from datetime import timedelta


class OfflineTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfflineTask
        fields = "__all__"


mandatory_fields = [
    "real_start", "real_end", "date_start", "activity_type", "date_end"]


class ActivitySerializer(serializers.ModelSerializer):
    real_start = serializers.SerializerMethodField()
    real_end = serializers.SerializerMethodField()
    date_end = serializers.SerializerMethodField()
    activity_type = serializers.SerializerMethodField()
    reals = (5, 10)
    start_field = "date_start"

    def get_real_start(self, obj):
        start = getattr(obj, self.start_field)
        return start - timedelta(minutes=self.reals[0])

    def get_real_end(self, obj):
        end = self.get_date_end(obj)
        return end + timedelta(minutes=self.reals[1])

    def get_date_end(self, obj):
        # date_start
        # date_end

        end = None
        if hasattr(obj, "date_end"):
            end = getattr(obj, "date_end")
        if not end:
            end = getattr(obj, self.start_field)
            end += timedelta(seconds=5)
        return end


class ScrapedRecordActivitySerializer(ActivitySerializer):

    def get_activity_type(self, obj):
        return "task"

    class Meta:
        model = ScrapedRecord
        fields = mandatory_fields


class ClickHistoryActivitySerializer(ActivitySerializer):
    reals = (3, 8)
    date_start = serializers.DateTimeField(source="date", read_only=True)
    model = serializers.SerializerMethodField()

    def get_model(self, obj):
        models = ["note", "article", "project", "mention", "location"]
        for model in models:
            if getattr(obj, model, None) is not None:
                return model

    def get_activity_type(self, obj):
        return obj.action

    class Meta:
        model = ClickHistory
        fields = mandatory_fields + ["model"]


class OfflineTaskActivitySerializer(ActivitySerializer):
    reals = (8, 12)
    offline_type = serializers.CharField(source="activity_type")

    def get_activity_type(self, obj):
        return "offline"

    class Meta:
        model = OfflineTask
        fields = mandatory_fields + ["name", "offline_type"]
