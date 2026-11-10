from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.request import Request, clone_request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.views.generic_merge.serializers import MergeSerializer
from ps_schema.registry import schema_for_model, viewset_for_model
from utils.register_merge import RecordMerger


def merge_denied(request: Request, model: type,
                 merge_id: int) -> str | None:
    """Why this user may not merge these two entries, or None.

    No rule of its own: the merge asks the model's own ViewSet exactly
    what a destroy of the absorbed entry would. The survivor is not
    checked as an update, so an open entry can be folded into a
    validated one by whoever may delete the open one.
    """
    schema = schema_for_model(model)
    if not schema or not schema.can_merge:
        return f"«{model._meta.verbose_name}» no admite fusiones."
    obj = model.objects.filter(pk=merge_id).first()
    if obj is None:
        # RecordMerger reports the missing entry.
        return None
    view = viewset_for_model(model)(action="destroy", format_kwarg=None)
    view.args, view.kwargs = (), {"pk": merge_id}
    view.request = clone_request(request, "DELETE")
    try:
        view.check_permissions(view.request)
        view.check_object_permissions(view.request, obj)
    except APIException:
        return (f"No tienes permiso para fusionar «{obj}» "
                f"(#{merge_id}) en esta colección.")
    except AttributeError:
        # The status rules read `status_validation.open_editor`; an entry
        # whose status is null breaks its destroy too, for anyone.
        return (f"«{obj}» (#{merge_id}) no tiene estatus de validación: "
                f"asígnale uno antes de fusionarla.")
    return None


class MergeRecordsView(APIView):
    """Merge two entries of a mergeable collection or catalog."""
    serializer_class = MergeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:

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

        # Same body as the merge errors: the dashboard shows `errors`.
        denied = merge_denied(request, merger.model_class, merge_id)
        if denied:
            return Response(
                {"errors": [denied]}, status=status.HTTP_403_FORBIDDEN)

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
