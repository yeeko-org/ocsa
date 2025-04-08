from rest_framework import serializers
from df.models import Dimension, PopulationSize, Temporality


class DimensionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dimension
        fields = '__all__'


class PopulationSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopulationSize
        fields = '__all__'


class TemporalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporality
        fields = '__all__'
