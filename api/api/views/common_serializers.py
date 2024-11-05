from rest_framework import serializers


class CommonCount(serializers.ModelSerializer):
    count = serializers.ReadOnlyField()
