from rest_framework import serializers
from df.models import Displacement, Dimension, PopulationSize


class DisplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = "__all__"


class DisplacementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Displacement
        fields = "__all__"


class DimensionSerializer(serializers.ModelSerializer):
    displacement_count = serializers.ReadOnlyField()

    class Meta:
        model = Dimension
        fields = '__all__'


class PopulationSizeSerializer(serializers.ModelSerializer):
    displacement_count = serializers.ReadOnlyField()

    class Meta:
        model = PopulationSize
        fields = '__all__'
