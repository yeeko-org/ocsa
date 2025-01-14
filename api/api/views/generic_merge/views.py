from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.generic_merge.serializers import MergeSerializer
from utils.register_merge import RecordMerger


class MergeRecordsView(APIView):
    serializer_class = MergeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        serializer = MergeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        model_name = serializer.validated_data['model_name']  # type:ignore
        main_id = serializer.validated_data['main_id']  # type:ignore
        merge_id = serializer.validated_data['merge_id']  # type:ignore
        delete_merge = serializer.validated_data['delete_merge']  # type:ignore
        just_report = serializer.validated_data['just_report']  # type:ignore

        try:
            merger = RecordMerger(model_name)
        except ValueError as e:
            raise ValidationError(str(e))

        merger.merge_registers(
            main_id, merge_id, delete_merge=delete_merge,
            just_report=just_report
        )

        response_data = {
            "report": merger.report,
            "errors": merger.errors,
            "deleted": merger.deleted_report
        }
        status_code = 200 if not merger.errors else 400

        return Response(response_data, status=status_code)
