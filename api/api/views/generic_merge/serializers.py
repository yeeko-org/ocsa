from rest_framework import serializers


class MergeSerializer(serializers.Serializer):
    model_name = serializers.CharField(required=True)
    main_id = serializers.IntegerField(required=True)
    merge_id = serializers.IntegerField(required=True)
    delete_merge = serializers.BooleanField(required=False, default=False)
    just_report = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        if data['main_id'] == data['merge_id']:
            raise serializers.ValidationError(
                "main_id y merge_id deben ser diferentes.")
        return data
