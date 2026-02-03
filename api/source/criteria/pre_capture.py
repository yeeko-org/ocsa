from typing import List, Type, Annotated
import json
from source.models import (
    Article, ScrapedRecord, Note)
from source.base_models import (
    NoteBase, NoteFull, MentionBase, EventBase, ImpactBase, ProjectDataBase,
    ActorBase, StatusHistoryBase, LocationFull, InterestFull)
from source.criteria import BaseCriteriaManager


class PreCaptureManager(BaseCriteriaManager):

    def __init__(
            self, recover_record: ScrapedRecord | None = None,
            ai_engine: str | None = None, is_test: bool = False
    ) -> None:
        super().__init__(recover_record, ai_engine, is_test)
        self.prompt_name = "pre_capture"
        self.seconds_cache = 10

    def get_articles_objects(self) -> List[Article]:
        articles = Article.objects.filter(
            scraped=self.scraped_record,
            second_certainty_degree__gt=100,
            note__isnull=True,
        )
        return list(articles)

    def get_full_content(self, article: Article) -> tuple[str, int]:
        init_content, p_idx = super().get_full_content(article)
        date = article.published_date.strftime('%d/%m/%Y')
        content = f"Fecha de la nota: {date}\n\n{init_content}"
        return content, p_idx

    def get_schema_class(self, p_count: int) -> Type[NoteBase]:
        import enum
        from pydantic import Field, BaseModel
        from impact.models import ImpactType
        from classify.models import Belong
        # from space_time.models import State

        # states = State.objects.all().values_list("short_name", flat=True)
        # StatesEnum = enum.Enum("StatesEnum", { state: state for state in states })
        impact_types = ImpactType.objects.filter(
            status_validation_id='validated')
        impact_type_dict = {it.name: it.name for it in impact_types}
        ImpactTypeEnum = enum.Enum(
            "ImpactTypeEnum", impact_type_dict)

        belongs = Belong.objects.all().values_list("name", flat=True)
        belongs_dict = {b: b for b in belongs}
        BelongsEnum = enum.Enum("BelongsEnum", belongs_dict)

        # bounded_int = List[Annotated[int, Field(ge=1, le=p_count)]]
        class ParagraphReference(BaseModel):
            paragraphs: List[Annotated[int, Field(ge=1, le=p_count)]] = Field(
                default_factory=list)

        class ProjectDataFinal(ParagraphReference, ProjectDataBase):
            pass

        class ImpactFinal(ParagraphReference, ImpactBase):
            impact_type_str: ImpactTypeEnum

        class EventFinal(ParagraphReference, EventBase):
            pass

        class ActorFinal(ParagraphReference, ActorBase):
            belongs_str: List[BelongsEnum] = []

        class StatusHistoryFinal(ParagraphReference, StatusHistoryBase):
            pass

        class FinalMentionBase(MentionBase):
            project_full: ProjectDataFinal
            impacts: List[ImpactFinal]
            events: List[EventFinal]
            actors: List[ActorFinal]
            status_history: List[StatusHistoryFinal]

        class FinalNoteBase(NoteBase):
            root: List[FinalMentionBase]

        # model_schema = FinalNoteBase.model_json_schema()
        return FinalNoteBase

    def get_additional_content(self, article: Article) -> str:
        additional = ""

        if article.second_criteria:
            additional += "\n\n{'=' * 30}\n"
            additional = "Lista de proyectos a identificar:\n"
            projects = article.second_criteria.get("projects", [])
            for (index, project) in enumerate(projects, start=1):
                if project.get("degrees", 0) > 100:
                    additional += f"index {index}: {project.get('name', '')}\n"

            additional += json.dumps(article.second_criteria)

        return additional

    def save_criteria_results(
            self, criteria: any, json_criteria: dict | list | None, article: Article
    ) -> None:
        from source.base_models import (
            position_mapping, event_group_mapping, impact_group_mapping)
        from classify.models import Belong, ParticipantGroup
        from space_time.models import State, Municipality, Locality
        from impact.models import ImpactType
        from project.models import StatusProject

        belongs_dict = {b.name: b.id for b in Belong.objects.all()}
        states_dict = {st.short_name: st.id for st in State.objects.all()}
        # position_dict = {pm.name: pm.id for pm in ParticipantGroup.objects.all()}
        impact_types_dict = {it.name: it.id for it in ImpactType.objects.all()}
        status_project_dict = {sp.name: sp.id for sp in StatusProject.objects.all()}

        # full_pre_capture = NoteFull(root=json_criteria)
        if not json_criteria:
            json_criteria = article.pre_capture
        full_pre_capture = NoteFull(root=json_criteria)
        # print("full_pre_capture\n", full_pre_capture.model_dump_json())

        def map_locations(locations: List[LocationFull]) -> List[LocationFull]:
            for location in locations:
                add_query = {}
                if location.state_str:
                    state_id = states_dict.get(location.state_str.value)
                    if state_id:
                        location.state = state_id
                        add_query['state_id'] = state_id
                    else:
                        location.details += f" (Estado: {location.state_str.value})"
                if location.municipality_text:
                    try:
                        municipality = Municipality.objects.get(
                            name__iexact=location.municipality_text,
                            **add_query
                        )
                        location.municipality = municipality.id
                        add_query['municipality_id'] = municipality.id
                    except Municipality.DoesNotExist:
                        location.details += f" (Municipio: {location.municipality_text})"
                if loc_text := location.locality_text:
                    locality = None
                    if hasattr(add_query, 'municipality_id'):
                        try:
                            locality = Locality.objects.get(
                                name__iexact=loc_text,
                                **add_query
                            )
                            location.locality = locality.id
                        except Locality.DoesNotExist:
                            pass
                    if not locality:
                        location.details += f" (Localidad: {loc_text})"
            return locations

        for mention in full_pre_capture.root:
            for actor in mention.actors:
                actor.belongs = [
                    belongs_dict.get(b_str) for b_str in actor.belongs_str
                ]
                actor.participant_group = position_mapping.get(
                    actor.position_str.name, None)
                actor.interests = [InterestFull(text=actor.interest_text)]

            for impact in mention.impacts:
                impact.impact_type = impact_types_dict.get(
                    impact.impact_type_str)
                impact.impact_group = impact_group_mapping.get(
                    impact.impact_group_str.name, None)
                impact.locations = map_locations(impact.locations)

            for event in mention.events:
                event_map = event_group_mapping.get(
                    event.event_group_str.name, None)
                if event_map:
                    event.event_group = event_map["event_group"]
                    event.purpose = event_map.get("purpose", None)
                event.locations = map_locations(event.locations)

            for status_history in mention.status_history:
                if status_his := status_project_dict.get(
                        status_history.status_project_str):
                    status_history.status_project = status_his

            mention.project_full.locations = map_locations(
                mention.project_full.locations)

        # print("full_pre_capture\n", full_pre_capture.model_dump_json())
        json_final = self.get_json_data(full_pre_capture)
        full_pre_capture = NoteFull.model_validate_with_paths(json_final)

        json_pre_capture = self.get_json_data(full_pre_capture)
        # article.pre_capture = json_pre_capture
        # article.save()
        self.save_related_note(article, json_pre_capture)

    def save_related_note(self, article: Article, json_pre_capture: list) -> None:
        note: Note = article.create_note_from_article()
        if not note.mentions.exists() and not note.frozen_pre_capture:
            print("Saving pre_capture to note id:", note.id)
            note.pre_mentions = json_pre_capture
            note.save()
