from typing import List, Type, Annotated
from source.models import Article
from source.criteria import BaseCriteriaManager
from profile_auth.models import User

# EventGroup.id del grupo "Mecanismos legales" (ver skill ocs-entities y
# event_group_mapping en source/base_models.py).
LEGAL_GROUP_ID = 3
NON_LEGAL_GROUPS = {"acts_of_violence", "collective_actions"}


class ReclassifyLegalManager(BaseCriteriaManager):
    """Reclasifica eventos marcados `reclassification_stage='pending'`
    al tipo correcto del grupo "Mecanismos legales", usando la nota
    como contexto. No crea Note/Mention: solo corrige FKs existentes.
    """

    prompt_name = "reclassify_legal"
    version = "v2"
    seconds_cache = 15

    def __init__(
            self, ai_engine: str | None = None, is_test: bool = False,
            user: User | None = None, prompt_version: str | None = None
    ) -> None:
        super().__init__(None, ai_engine, is_test, prompt_version)
        self.user = user

    # ------------------------------------------------------------------
    # Selección de trabajo
    # ------------------------------------------------------------------
    def get_articles_objects(self) -> List[Article]:
        articles = Article.objects\
            .filter(
            note__mentions__events__reclassification_stage='pending',
            paragraphs__isnull=False)\
            .exclude(paragraphs=[])\
            .order_by('note_id', '-id')\
            .distinct('note_id')
        return list(articles)

    def _pending_events(self, article: Article) -> list:
        from event.models import Event
        return list(Event.objects.filter(
            mention__note_id=article.note_id,
            reclassification_stage='pending',
        ).select_related('event_type', 'mention__project'))

    def _classified_legal_events(self, article: Article) -> list:
        from event.models import Event
        return list(Event.objects.filter(
            mention__note_id=article.note_id,
            event_type__event_group_id=LEGAL_GROUP_ID,
        ).exclude(
            reclassification_stage='pending'
        ).select_related('event_type', 'purpose', 'mention__project'))

    def _project_name(self, ev) -> str:
        proj = ev.mention.project
        return proj.name or f"Proyecto #{proj.id}"

    # ------------------------------------------------------------------
    # Prompt cacheado: catálogo inyectado en el system_msg
    # ------------------------------------------------------------------
    def get_extra_system_msg(self) -> str:
        return self._build_catalog_block()

    def _build_catalog_block(self) -> str:
        from event.models import EventType
        legals = EventType.objects.filter(
            event_group_id=LEGAL_GROUP_ID,
            status_validation_id='validated',
        ).order_by('order', 'name')
        lines = ["## CATÁLOGO DE MECANISMOS LEGALES (elige solo de aquí)"]
        for et in legals:
            desc = (et.description or "").strip()
            lines.append(f"- {et.name}: {desc}")

        others = EventType.objects.exclude(
            status_validation_id='need_reclassify'
        ).order_by('order', 'name')
        violences = "; ".join(
            e.name for e in others if e.event_group_id == 1)
        collectives = "; ".join(
            e.name for e in others if e.event_group_id == 2)
        lines.append(
            f"\n## TIPOS DE VIOLENCIA (NO son mecanismo legal): {violences}")
        lines.append(
            f"## ACCIONES COLECTIVAS (NO son mecanismo legal): {collectives}")
        return "\n".join(lines)

    def get_additional_content(self, article: Article) -> str:
        events = self._pending_events(article)
        if not events:
            return ""
        lines = ["\n## EVENTOS A RECLASIFICAR EN ESTA NOTA"]
        for ev in events:
            desc = (ev.description or "").strip()
            lines.append(
                f"- event_id {ev.id} "
                f"| proyecto: {self._project_name(ev)} "
                f"| descripción actual: {desc}")

        classified = self._classified_legal_events(article)
        if classified:
            lines.append(
                "\n## EVENTOS LEGALES YA CLASIFICADOS EN ESTA NOTA "
                "(no los dupliques)")
            for ev in classified:
                purpose = ev.purpose.name if ev.purpose else "sin propósito"
                lines.append(
                    f"- {ev.event_type.name} ({purpose}) "
                    f"— proyecto: {self._project_name(ev)}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Esquema de respuesta: Enum dinámico de los 18 tipos validated
    # ------------------------------------------------------------------
    def get_schema_class(self, p_count: int) -> Type:
        import enum
        from pydantic import Field, RootModel
        from event.models import EventType
        from source.base_models import LegalReclassifyItemBase

        legals = EventType.objects.filter(
            event_group_id=LEGAL_GROUP_ID,
            status_validation_id='validated',
        )
        legal_enum_dict = {et.name: et.name for et in legals}
        LegalEventTypeEnum = enum.Enum("LegalEventTypeEnum", legal_enum_dict)

        class LegalReclassifyItemFinal(LegalReclassifyItemBase):
            event_type_str: LegalEventTypeEnum | None = None
            paragraphs: List[Annotated[int, Field(ge=0, le=p_count)]] = []

        class LegalReclassifyResultFinal(RootModel):
            root: List[LegalReclassifyItemFinal] = []

        return LegalReclassifyResultFinal

    # ------------------------------------------------------------------
    # Guardado: solo corrige el Event, con snapshot original
    # ------------------------------------------------------------------
    def save_criteria_results(
            self, criteria: any, json_criteria: dict | list | None,
            article: Article
    ) -> None:
        from django.utils import timezone
        from event.models import EventType
        from source.base_models import purpose_mapping

        pending = {ev.id: ev for ev in self._pending_events(article)}
        if not pending:
            return

        legal_types = {
            et.name: et.id for et in EventType.objects.filter(
                event_group_id=LEGAL_GROUP_ID,
                status_validation_id='validated')}

        for item in criteria.root:
            event = pending.get(item.event_id)
            if not event:
                print(f"event_id {item.event_id} no pendiente; se omite")
                continue

            actual_group = (
                item.actual_group_str.value
                if item.actual_group_str else None)
            et_value = (
                item.event_type_str.value
                if item.event_type_str else None)
            purpose_value = (
                item.purpose_str.value
                if item.purpose_str else None)
            event.reclassification_data = {
                "original": {
                    "event_type_id": event.event_type_id,
                    "event_type": (
                        event.event_type.name
                        if event.event_type else None),
                    "event_group_id": (
                        event.event_type.event_group_id
                        if event.event_type else None),
                    "purpose_id": event.purpose_id,
                    "description": event.description,
                },
                "ai": {
                    "event_type": et_value,
                    "purpose": purpose_value,
                    "confidence": item.confidence,
                    "description": item.description,
                    "actual_group": actual_group,
                },
                "reclassified_at": timezone.now().isoformat(),
            }
            event.reclassification_confidence = item.confidence

            new_type_id = legal_types.get(et_value)
            if actual_group in NON_LEGAL_GROUPS or not new_type_id:
                event.reclassification_stage = 'problematic'
                event.save()
                continue

            event.event_type_id = new_type_id
            event.purpose_id = purpose_mapping.get(purpose_value)
            event.description = item.description
            event.reclassification_stage = 'reclassified'
            event.save()