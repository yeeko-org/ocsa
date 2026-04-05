from api.export_blocks.base import ExportBlock
from api.export_blocks.actor import ActorExportBlock


class ParticipantExportBlock(ExportBlock):
    """Columnas y extractor para Participant en exportaciones XLSX.

    Incluye datos del actor embebidos via ActorExportBlock.prefixed("actor").
    No incluye datos de evento/involucramiento ni de mención — esos los
    aporta el ViewSet según su contexto.

    Requiere select_related:
        actor, actor__parent_actor, actor__sector,
        actor__sector__sector_group, actor__indigenous_group.
    Requiere prefetch_related:
        participant_types, participant_types__participant_group,
        interests, interests__interest_subtype,
        interests__interest_subtype__interest_type,
        interests__interest_subtype__interest_type__interest_group,
        actor__belongs, actor__countries.
    """

    columns = [
        {"name": "ID de participante", "width": 7, "field": "id"},
        *ActorExportBlock.prefixed("actor"),
        {"name": "Posición en el proyecto", "width": 20,
         "field": "participant_groups"},
        {"name": "Tipos de participación", "width": 20,
         "field": "participant_types"},
        {"name": "Grupo de interés", "width": 30, "field": "interest_groups",
         "conditions": ["only_logged_in"]},
        {"name": "Tipo de interés", "width": 30, "field": "interest_types",
         "conditions": ["only_logged_in"]},
        {"name": "Subtipo de interés", "width": 30,
         "field": "interest_subtypes", "conditions": ["only_logged_in"]},
        {"name": "Descripción del interés", "width": 40, "field": "interests"},
    ]

    @classmethod
    def extract(cls, participant) -> dict:
        from api.views.common_serializers import extract_interests
        pt_list = list(participant.participant_types.all())
        return {
            "id": participant.id,
            "actor": ActorExportBlock.extract(participant.actor),
            "participant_groups": [
                pt.participant_group.name for pt in pt_list],
            "participant_types": [pt.name for pt in pt_list],
            **extract_interests(participant),
        }