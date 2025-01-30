from rest_framework import serializers
from df.models import Dimension, PopulationSize


class DimensionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dimension
        fields = '__all__'


class PopulationSizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopulationSize
        fields = '__all__'
