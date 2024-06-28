from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist


class FromToModelSerializer(serializers.Serializer):
    from_id = serializers.IntegerField()
    delete = serializers.BooleanField(default=True, required=False)


class MergeSerializerMixin(viewsets.GenericViewSet):
    def get_serializer_class(self):
        if self.action == 'merge':
            return FromToModelSerializer
        return self.serializer_class

    def get_from_obj(self, from_id):
        raise NotImplementedError

    def update_relations_merge(self, from_obj, to_obj):
        raise NotImplementedError

    @action(detail=True, methods=['post'])
    def merge(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        from_id = data['from_id']
        delete = data.get('delete', True)

        try:
            from_obj = self.get_from_obj(from_id)
        except ObjectDoesNotExist:
            return Response({'message': 'From Obj not found'}, status=404)

        self.update_relations_merge(from_obj, obj)

        if delete:
            from_obj.delete()

        return Response({'message': 'Merged successfully'})
