from rest_framework import viewsets

from actor.models import Participant
from api.export_blocks.event import EventExportBlock
from api.export_blocks.participant import ParticipantExportBlock
from api.views.action_export_xls import ExportXlsMixin


_EMPTY_EVENT_EXTRACT = {
    "id": "",
    "event_type": {"event_group": "", "name": ""},
    "description": "",
    "number_women": "",
    "number_men": "",
    "number_mix": "",
    "purpose": "",
}


class ParticipationExportViewSet(ExportXlsMixin, viewsets.GenericViewSet):
    """
    Exportación conjunta de participación.

    Combina en un solo archivo XLS:
    - Participantes con involucramiento en eventos (una fila por evento).
    - Participantes sin involucramiento (una fila con evento vacío).

    La expansión 1→N ocurre en get_export_rows(): cada Participant genera
    tantas filas como Involved tenga, o una fila vacía si no tiene ninguno.
    """

    queryset = Participant.objects.none()
    xls_name = "Participación"
    xls_attrs = [
        {"name": "ID de mención", "width": 7, "field": "mention_id"},
        {"name": "Consecutivo", "width": 5, "field": "consecutive"},
        {"special_group": "participant"},
        {"special_group": "event", "preset": "event"},
        {"name": "Rol en el evento", "width": 20, "field": "involved_role"},
        {"special_group": "mention"},
    ]

    def get_query_for_export_xls(self):
        return (
            Participant.objects.all()
            .select_related(
                "mention",
                "mention__note",
                "mention__note__source",
                "mention__project",
                "mention__project__conflict",
                "actor",
                "actor__parent_actor",
                "actor__sector",
                "actor__sector__sector_group",
                "actor__indigenous_group",
            )
            .prefetch_related(
                "participant_types",
                "participant_types__participant_group",
                "interests",
                "interests__interest_subtype",
                "interests__interest_subtype__interest_type",
                "interests__interest_subtype__interest_type__interest_group",
                "actor__belongs",
                "actor__countries",
                "involvements",
                "involvements__event",
                "involvements__event__event_type",
                "involvements__event__event_type__event_group",
                "involvements__event__purpose",
                "involvements__involved_role",
            )
            .order_by("mention_id")
            .distinct()
        )

    def get_export_rows(self, queryset) -> list[dict]:
        from api.export_blocks.mention import MentionExportBlock

        rows = []
        for participant in queryset:
            base = {
                "mention_id": participant.mention.id,
                **ParticipantExportBlock.extract(participant),
                **MentionExportBlock.extract(participant),
            }
            involvements = list(participant.involvements.all())
            if not involvements:
                rows.append({
                    **base,
                    "consecutive": 1,
                    "event": _EMPTY_EVENT_EXTRACT,
                    "involved_role": "",
                })
            else:
                for i, inv in enumerate(involvements, start=1):
                    rows.append({
                        **base,
                        "consecutive": i,
                        "event": EventExportBlock.extract(inv.event),
                        "involved_role": (
                            inv.involved_role.name
                            if inv.involved_role else ""),
                    })
        return rows