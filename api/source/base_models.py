import enum
import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, RootModel, model_validator
from functools import wraps


class ExtractivismTypes(enum.Enum):
    agro = "agro"
    mineria = "mineria"
    hidricos = "hidricos"
    energia = "energia"
    urbano = "urbano"
    infra = "infra"


class ProjectBase(BaseModel):
    name: str
    types: list[ExtractivismTypes] = []
    paragraphs: list[int] = []


class FeaturesBase(BaseModel):
    opponents: list[int]
    social_impacts: list[int]
    ecological_impacts: list[int]
    acts_of_violence: list[int]
    collective_actions: list[int]


class ProjectSelect(ProjectBase, FeaturesBase):
    is_specific_project: bool
    is_extractivist_or_big_scale: bool
    is_public_policy: bool
    is_political_opinion: bool
    is_labor_conflict_only: bool


class ArticleBase(FeaturesBase):
    projects: list[ProjectBase] = []
    is_foreign: bool | None = None
    is_political_opinion: bool | None = None


class ArticleRevision(BaseModel):
    projects: list[ProjectSelect] = []


class StateEnum(enum.Enum):
    aguascalientes = "Aguascalientes"
    baja_california = "Baja California"
    baja_california_sur = "Baja California Sur"
    campeche = "Campeche"
    coahuila = "Coahuila"
    colima = "Colima"
    chiapas = "Chiapas"
    chihuahua = "Chihuahua"
    ciudad_de_mexico = "Ciudad de México"
    durango = "Durango"
    guanajuato = "Guanajuato"
    guerrero = "Guerrero"
    hidalgo = "Hidalgo"
    jalisco = "Jalisco"
    mexico = "México"
    michoacan = "Michoacán"
    morelos = "Morelos"
    nayarit = "Nayarit"
    nuevo_leon = "Nuevo León"
    oaxaca = "Oaxaca"
    puebla = "Puebla"
    queretaro = "Querétaro"
    quintana_roo = "Quintana Roo"
    san_luis_potosi = "San Luis Potosí"
    sinaloa = "Sinaloa"
    sonora = "Sonora"
    tabasco = "Tabasco"
    tamaulipas = "Tamaulipas"
    tlaxcala = "Tlaxcala"
    veracruz = "Veracruz"
    yucatan = "Yucatán"
    zacatecas = "Zacatecas"
    no_identified = "No identificado"


event_group_mapping = {
    "acts_of_violence": {"event_group": 1},
    "collective_actions": {"event_group": 2},
    "spoliation_acts": {"event_group": 3, "purpose": 1},
    "defense_acts": {"event_group": 3, "purpose": 2},
}

class EventGroupEnum(enum.Enum):
    # collective_actions = "Acciones colectivas"
    # acts_of_violence = "Violencias"
    # spoliation_acts = "Mecanismos legales de despojo"
    # defense_acts = "Mecanismos legales de defensa"
    collective_actions = "collective_actions"
    acts_of_violence = "acts_of_violence"
    spoliation_acts = "spoliation_acts"
    defense_acts = "defense_acts"


position_mapping = {
    "oppose": 1,
    "support": 3,
    "neutral": 2,
}


class PositionEnum(enum.Enum):
    # oppose = "En contra del proyecto"
    # support = "A favor del proyecto"
    # neutral = "Mediador"
    oppose = "oppose"
    support = "support"
    neutral = "neutral"


impact_group_mapping = {
    "social": 1,
    "ecological": 2,
}


class PathMixin:
    """Mixin para añadir funcionalidad de JSONPath"""
    _current_path: Optional[str] = None

    @classmethod
    def _set_paths_recursive(cls, data: Any, path: str = "$") -> Any:
        """Añade paths recursivamente a estructuras de datos"""
        if isinstance(data, dict):
            # Añadir path si existe el campo
            if 'path' in data:
                data['path'] = path

            # Procesar recursivamente
            for key, value in list(data.items()):
                new_path = f"{path}.{key}"
                if isinstance(value, list):
                    data[key] = [
                        cls._set_paths_recursive(item, f"{new_path}[{i}]")
                        for i, item in enumerate(value)
                    ]
                elif isinstance(value, dict):
                    data[key] = cls._set_paths_recursive(value, new_path)

        elif isinstance(data, list):
            return [
                cls._set_paths_recursive(item, f"{path}[{i}]")
                for i, item in enumerate(data)
            ]

        return data


class ImpactGroupEnum(enum.Enum):
    # social = "Social"
    # ecological = "Ambiental"
    social = "social"
    ecological = "ecological"


class CommonFull(BaseModel, PathMixin):
    element_id: int | None = None
    discarded: bool | None = None
    path: str | None = None


class LocationBase(BaseModel):
    state_str: StateEnum
    municipality_text: str | None = None
    locality_text: str | None = None
    details: str | None
    paragraphs: list[int] = []


class LocationFull(LocationBase, CommonFull):
    state: int | None = None
    municipality: int | None = None
    locality: int | None = None
    details: str | None = ""
    status_location: str = "initial"


class ProjectDataBase(BaseModel):
    index: int
    name: str
    project_type_text: str
    parent_project_text: str | None
    locations: list[LocationBase] = []
    paragraphs: list[int] = []


class ProjectDataFull(ProjectDataBase, PathMixin):
    extractivism_types_str: list[str] = []
    extractivism_types: list[int] = []
    locations: list[LocationFull] = []
    hide_mention: bool = True
    path: str | None = None


class StatusHistoryBase(BaseModel):
    date: datetime.date
    status_project_text: str = Field(max_length=100)
    paragraphs: list[int] = []


class StatusHistoryFull(StatusHistoryBase, CommonFull):
    status_project: int | None = None


class ImpactBase(BaseModel):
    impact_group_str: ImpactGroupEnum
    impact_type_str: str
    description: str = Field(max_length=300)
    is_potential: bool
    locations: list[LocationBase] = []
    paragraphs: list[int] = []


class ImpactFull(ImpactBase, CommonFull):
    impact_group: int | None = None
    impact_type: int | None = None
    locations: list[LocationFull] = []


class InterestFull(CommonFull):
    text: str = ""
    interest_group: int = 1
    interest_type: int = 1


class ActorBase(BaseModel):
    uid: int = Field(gt=0, lt=21)
    name: str
    sector_text: str = Field(max_length=100)
    belongs_str: list[str] = []
    position_str: PositionEnum
    interest_text: str = Field(max_length=300)
    paragraphs: list[int] = []


# class ActorFull(ActorBase, CommonFull):
#     participant_group: int | None = None
#     belongs: list[int] = []
#     interests: list[InterestFull] = []


class FinalActorFull(BaseModel, PathMixin):
    uid: int = Field(gt=0, lt=21)
    name: str
    sector_text: str = Field(max_length=100)
    belongs: list[int] = []
    path: str | None = None
    status_validation: str = 'yk_proposed'
    paragraphs: list[int] = []


class ParticipantFull(CommonFull):
    participant_group: int | None = None
    interests: list[InterestFull] = []
    actor_full: FinalActorFull | None = None
    paragraphs: list[int] = []


class InvolvementBase(BaseModel):
    actor_uid: int = Field(gt=0, lt=21)
    role_text: str = Field(max_length=80)


class InvolvementFull(InvolvementBase, CommonFull):
    pass


class EventBase(BaseModel):
    event_group_str: EventGroupEnum
    description: str = Field(max_length=300)
    # involvements_text: list[str] = []
    involvements: list[InvolvementBase] = []
    locations: list[LocationBase] = []
    paragraphs: list[int] = []


class EventFull(EventBase, CommonFull):
    event_group: int | None = None
    purpose: int | None = None
    locations: list[LocationFull] = []
    involvements: list[InvolvementFull] = []


class MentionBase(BaseModel):
    project_full: ProjectDataBase
    status_history: list[StatusHistoryBase] = []
    impacts: list[ImpactBase] = []
    actors: list[ActorBase] = []
    events: list[EventBase] = []


class MentionFull(MentionBase, CommonFull):
    project_full: ProjectDataFull
    status_history: list[StatusHistoryFull] = []
    impacts: list[ImpactFull] = []
    # actors: list[ActorFull] = Field(max_length=20, default=[])
    participants: list[ParticipantFull] = []
    events: list[EventFull] = []
    note: int | None = None


class NoteBase(RootModel):
    root: list[MentionBase] = []


class NoteHydrated(RootModel, PathMixin):
    root: list[MentionFull] = []

    # @classmethod
    # def from_dict_with_paths(cls, data: list[dict]) -> 'NoteFull':
    #     """Crea instancia con paths automáticos"""
    #     data_with_paths = cls._set_paths_recursive(data, "$")
    #     return cls(root=data_with_paths)

    @classmethod
    def model_validate_with_paths(cls, data: list) -> 'NoteHydrated':
        if isinstance(data, list):
            data = cls._set_paths_recursive(data, "$")
        # return cls.model_validate(
        #     { "root": data } if isinstance(data, list) else data)
        return cls.model_validate(data)
