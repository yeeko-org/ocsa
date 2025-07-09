
all_available_actions = [
    "massive_delete",
    "merge",
    "massive_edit",
]

all_collections = {
    "source": [
        {
            "snake_name": "note",
            "name": "Nota",
            "plural_name": "Notas",
            "model_name": "Note",
            "level": "primary",
            "color": 'deep-purple',
            "icon": 'newspaper',
            "all_filters": [
                {"filter_name": "source_types", "hidden": False},
                {
                    "title": "Fechas",
                    "component": "RangeDates", "hidden": False
                },
                {
                    "title": "Editor", "field": "editor",
                    "component": "UserSelect", "hidden": True
                },
                {
                    "title": "Revisor", "field": "reviewer",
                    "component": "UserSelect", "hidden": True
                },
                {
                    "title": "Con archivos", "field": "has_files",
                    "component": "TripleBooleanFilter", "hidden": True
                },
            ],
        },
        {
            "snake_name": "source",
            "name": "Fuente de información",
            "plural_name": "Fuentes de información",
            "model_name": "Source",
            "level": "category_subtype",
        },
        {
            "snake_name": "mention",
            "name": "Mención de proyecto en nota",
            "plural_name": "Menciones de proyectos en notas",
            "model_name": "Mention",
            "level": "relational",
        },
        {
            "snake_name": "status_history",
            "name": "Historial de estatus",
            "plural_name": "Historial de estatus",
            "model_name": "StatusHistory",
            "level": "secondary",
        },
        {
            "snake_name": "note_file",
            "name": "Archivo de nota",
            "plural_name": "Archivos de nota",
            "model_name": "NoteFile",
            "level": "relational",
        },
    ],
    "project": [
        {
            "snake_name": "project",
            "name": "Proyecto",
            "plural_name": "Proyectos",
            "model_name": "Project",
            "level": "primary",
            "icon": 'factory',
            "color": 'purple',
            "sort_fields": [
                'id', 'status_validation__order', 'name',
                'status_location__order'
            ],
            "all_filters": [
                {"filter_name": "project_types", "hidden": False},
                {"filter_name": "states", "hidden": False},
                {"filter_name": "status_projects", "hidden": True},
                {"filter_name": "impact_types", "hidden": True},
                {"filter_name": "event_types", "hidden": True},
                {
                    "title": "Es agrupador", "field": "is_grouper",
                    "component": "TripleBooleanFilter", "hidden": True
                },
            ],
            "xls_export": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "status_project",
            "name": "Status de Proyecto",
            "plural_name": "Status de Proyectos",
            "model_name": "StatusProject",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "extractivism_type",
            "name": "Tipo de Extractivismo",
            "plural_name": "Tipos de Extractivismo",
            "model_name": "ExtractivismType",
            "level": "category_type",
            "sort_fields": [
                # 'status_validation__order',
                'count',
                {'count': 'Cantidad de proyectos'},
            ],
        },
        {
            "snake_name": "megaproject_type",
            "name": "Tipo de Megaproyecto",
            "plural_name": "Tipos de Megaproyecto",
            "model_name": "MegaprojectType",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "conflict",
            "name": "Conflicto Socioambiental",
            "plural_name": "Conflictos Socioambientales",
            "model_name": "Conflict",
            "level": "primary",
            "icon": 'local_fire_department',
            "color": 'pink',
            "available_actions": ["merge"],
        },
        {
            "snake_name": "project_file",
            "name": "Archivo de proyecto",
            "plural_name": "Archivos de proyecto",
            "model_name": "ProjectFile",
            "level": "relational",
        },
        # {
        #     "snake_name": "project_location",
        #     "name": "Ubicación de Proyecto",
        #     "plural_name": "Ubicaciones de Proyecto",
        #     "model_name": "ProjectLocation",
        #     "level": "relational",
        # },
    ],
    "impact": [
        {
            "snake_name": "impact",
            "name": "Afectación",
            "plural_name": "Afectaciones",
            "model_name": "Impact",
            "level": "secondary",
            "color": 'indigo',
            "all_filters": [
                {"filter_name": "impact_types", "hidden": False},
            ],
            "available_actions": ["massive_edit"],
        },
        {
            "snake_name": "impact_group",
            "name": "Grupo de Afectación",
            "plural_name": "Grupos de Afectación",
            "model_name": "ImpactGroup",
            "level": "category_group",
        },
        {
            "snake_name": "impact_type",
            "name": "Tipo de Afectación",
            "plural_name": "Tipos de Afectación",
            "model_name": "ImpactType",
            "level": "category_type",
            "available_actions": ["merge"],
        },
        {
            "snake_name": "impact_subtype",
            "name": "Subtipo de Afectación",
            "plural_name": "Subtipos de Afectación",
            "model_name": "ImpactSubtype",
            "level": "category_subtype",
            "optional_category": True,
            "open_insertion": False,
            "available_actions": ["merge"],
        },
    ],
    "actor": [
        {
            "snake_name": "actor",
            "name": "Actor",
            "plural_name": "Actores",
            "model_name": "Actor",
            "level": "primary",
            "icon": 'recent_actors',
            "color": 'blue',
            "sort_fields": [
                'status_location__order', 'name',
                {'mentions_count': 'Cantidad de menciones'},
            ],
            "all_filters": [
                {"filter_name": "participant_types", "hidden": False},
                {"filter_name": "belongs", "hidden": False},
                {"filter_name": "indigenous_groups", "hidden": True},
                {"filter_name": "sectors", "hidden": False},
                {"filter_name": "countries", "hidden": True},
            ],
            "available_actions": ["merge"],
        },
        {
            "snake_name": "participant",
            "name": "Participante",
            "plural_name": "Participantes",
            "model_name": "Participant",
            "level": "relational",
        },
        {
            "snake_name": "interest",
            "name": "Interés",
            "plural_name": "Intereses",
            "model_name": "Interest",
            "level": "secondary",
            "color": "cyan",
            "available_actions": ["massive_edit"],
        },
    ],
    "classify": [
        {
            "snake_name": "participant_group",
            "name": "Tipo de Part.",
            "plural_name": "Tipos de Participación",
            "model_name": "ParticipantGroup",
            "level": "category_type",
        },
        {
            "snake_name": "participant_type",
            "name": "Subtipo de Part.",
            "plural_name": "Subtipos de Participación en Proyecto",
            "model_name": "ParticipantType",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "belong",
            "name": "Grupo de Pertenencia (Vulnerabilidad)",
            "plural_name": "Grupos de Pertenencia (Vulnerabilidades)",
            "model_name": "Belong",
            "level": "category_subtype",
            "open_insertion": False,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "indigenous_group",
            "name": "Pueblo Indígena",
            "plural_name": "Pueblos Indígenas",
            "model_name": "IndigenousGroup",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "sector_group",
            "name": "Grupo Sectorial",
            "plural_name": "Grupos Sectoriales",
            "model_name": "SectorGroup",
            "level": "category_type",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "sector",
            "name": "Sector",
            "plural_name": "Sectores",
            "model_name": "Sector",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "interest_group",
            "name": "Agrupador de tipos de interés",
            "plural_name": "Agrupadores de tipos de interés",
            "model_name": "InterestGroup",
            "level": "category_type",
        },
        {
            "snake_name": "interest_type",
            "name": "Tipo de interés",
            "plural_name": "Tipos de interés",
            "model_name": "InterestType",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "interest_subtype",
            "name": "Subtipo de interés",
            "plural_name": "Subtipos de interés",
            "model_name": "InterestSubtype",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "country",
            "name": "País",
            "plural_name": "Paises",
            "model_name": "Country",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
    ],
    "event": [
        {
            "snake_name": "event",
            "name": "Evento",
            "plural_name": "Eventos",
            "model_name": "Event",
            "level": "secondary",
            "icon": 'notifications_active',
            "color": 'lime',
            "all_filters": [
                {"filter_name": "event_types", "hidden": False},
                {"filter_name": "purposes", "hidden": True},
                # {"name": "involved_roles", "hidden": False},
            ],
            "xls_export": True,
            "available_actions": ["massive_edit"],
        },
        {
            "snake_name": "event_group",
            "name": "Grupo de Evento",
            "plural_name": "Grupos de Eventos",
            "model_name": "EventGroup",
            "open_insertion": False,
            "level": "category_group",
        },
        {
            "snake_name": "event_type",
            "name": "Tipo de Evento",
            "plural_name": "Tipos de Eventos",
            "model_name": "EventType",
            "level": "category_type",
            "open_insertion": True,
            "available_actions": ["merge", "massive_edit"],
        },
        {
            "snake_name": "event_subtype",
            "name": "Subtipo de Evento",
            "plural_name": "Subtipos de Eventos",
            "model_name": "EventSubtype",
            "level": "category_subtype",
            "open_insertion": True,
            "available_actions": ["merge"],
        },
        {
            "snake_name": "involved_role",
            "name": "Rol en Actividad",
            "plural_name": "Roles en Actividades",
            "model_name": "InvolvedRole",
            "open_insertion": False,
            "level": "category_subtype",
        },
        {
            "snake_name": "involved",
            "name": "Involucrado en Evento",
            "plural_name": "Involucrados en Eventos",
            "model_name": "Involved",
            "level": "relational",
        },
        {
            "snake_name": "purpose",
            "name": "Propósito del Mecanismo",
            "plural_name": "Propósitos de Mecanismos",
            "model_name": "Purpose",
            "level": "category_subtype",
        },
        # {
        #     "snake_name": "event_location",
        #     "name": "Ubicación de Evento",
        #     "plural_name": "Ubicaciones de Eventos",
        #     "model_name": "EventLocation",
        #     "level": "relational",
        # },
    ],
    "df": [
        {
            "snake_name": "displacement",
            "name": "Desplazamiento Forzado",
            "plural_name": "Desplazamientos Forzados",
            "model_name": "Displacement",
            "level": "primary",
            "icon": 'hiking',
            "color": 'orange',
            "all_filters": [
                {"filter_name": "dimensions", "hidden": False},
                {"filter_name": "population_sizes", "hidden": False},
                {"filter_name": "temporalities", "hidden": False},
                {
                    "title": "Colección", "field": "only_by",
                    "component": "OnlyByFilter", "hidden": False,
                    "options": ["event", "impact"]
                },
            ],
        },
        {
            "snake_name": "dimension",
            "model_name": "Dimension",
            "level": "category_subtype",
        },
        {
            "snake_name": "population_size",
            "model_name": "PopulationSize",
            "level": "category_subtype",
        },
        {
            "snake_name": "temporality",
            "model_name": "Temporality",
            "level": "category_subtype",
        },
    ],
    "space_time": [
        {
            "snake_name": "state",
            "name": "Estado",
            "plural_name": "Estados",
            "model_name": "State",
            "level": "category_group",
        },
        {
            "snake_name": "municipality",
            "name": "Municipio",
            "plural_name": "Municipios",
            "model_name": "Municipality",
            "level": "category_type",
        },
        {
            "snake_name": "locality",
            "name": "Localidad",
            "plural_name": "Localidades",
            "model_name": "Locality",
            "level": "category_subtype",
        },
        {
            "snake_name": "location",
            "name": "Ubicación",
            "plural_name": "Ubicaciones",
            "model_name": "Location",
            "level": "primary",
            "available_actions": ["massive_edit"],
            # "sort_fields": [
            #     'id', 'status_validation__order', 'name',
            #     'status_location__order'
            # ],
            "all_filters": [
                {"filter_name": "states", "hidden": False},
                {
                    "title": "Colección", "field": "only_by",
                    "component": "OnlyByFilter", "hidden": False,
                    "options": ["project", "event", "impact"]
                },
                {
                    "title": "Tipo de ubicación", "component": "LocationType",
                    "field": "type_location", "hidden": True,
                },
            ],
        },
    ]
}

filter_groups = [
    {
        "key_name": "source_types",
        "name": "Fuente de información",
        "plural_name": "Fuentes de información",
        "main_collection": "source-note",
        "category_subtype": "source-source",
    },
    {
        "key_name": "project_types",
        "name": "Clasificación de Proyecto",
        "short_name": "Clasif. de Proyecto",
        "plural_name": "Clasificaciones de Proyecto",
        "main_collection": "project-project",
        "category_type": "project-extractivism_type",
        "category_subtype": "project-megaproject_type",
    },
    {
        "key_name": "participant_types",
        "name": "Tipo de Participación",
        "plural_name": "Tipos de Participación",
        "main_collection": "actor-actor",
        "category_type": "classify-participant_group",
        "category_subtype": "classify-participant_type",
    },
    {
        "key_name": "belongs",
        "name": "Grupo de Pertenencia",
        "plural_name": "Grupos de Pertenencia",
        "main_collection": "actor-actor",
        "category_subtype": "classify-belong",
        "addl_config": {"item_id": "key_name"},
    },
    {
        "key_name": "indigenous_groups",
        "name": "Grupo Indígena",
        "plural_name": "Grupos Indígenas",
        "main_collection": "actor-actor",
        "category_subtype": "classify-indigenous_group",
    },
    {
        "key_name": "sectors",
        "name": "Sector",
        "plural_name": "Sectores",
        "main_collection": "actor-actor",
        "category_type": "classify-sector_group",
        "category_subtype": "classify-sector",
    },
    {
        "key_name": "interest_types",
        "name": "Tipo de interés",
        "plural_name": "Tipos de interés",
        "main_collection": "actor-interest",
        "category_group": "classify-interest_group",
        "category_type": "classify-interest_type",
        "category_subtype": "classify-interest_subtype",
        "addl_config": {
            "short_prev": "Int.",
            "prev": "Interés",
        },
    },
    {
        "key_name": "event_types",
        "name": "Clasificación de Evento",
        "plural_name": "Clasificaciones de Eventos",
        "main_collection": "event-event",
        "category_group": "event-event_group",
        "category_type": "event-event_type",
        "category_subtype": "event-event_subtype",
        "addl_config": {
            "short_prev": "Ev.",
            "prev": "Evento",
        },
    },
    {
        "key_name": "involved_roles",
        "name": "Rol en Actividad",
        "plural_name": "Roles en Actividades",
        "main_collection": "event-event",
        "category_subtype": "event-involved_role",
    },
    {
        "key_name": "purposes",
        "name": "Propósito",
        "plural_name": "Propósitos",
        "main_collection": "event-event",
        "category_subtype": "event-purpose",
    },
    {
        "key_name": "impact_types",
        "name": "Clasificación de Afectación",
        "plural_name": "Clasificaciones de Afectación",
        "main_collection": "impact-impact",
        "category_group": "impact-impact_group",
        "category_type": "impact-impact_type",
        "category_subtype": "impact-impact_subtype",
        "addl_config": {
            "short_prev": "Af.",
            "prev": "Afectación",
        },
    },
    {
        "key_name": "dimensions",
        "name": "Dimensión",
        "plural_name": "Dimensiones",
        "main_collection": "df-displacement",
        "category_subtype": "df-dimension",
    },
    {
        "key_name": "population_sizes",
        "name": "Tamaño de Población",
        "plural_name": "Tamaños de Población",
        "main_collection": "df-displacement",
        "category_subtype": "df-population_size",
    },
    {
        "key_name": "temporalities",
        "name": "Temporalidad",
        "plural_name": "Temporalidades",
        "main_collection": "df-displacement",
        "category_subtype": "df-temporality",
    },
    {
        "key_name": "countries",
        "name": "País",
        "plural_name": "Paises",
        "main_collection": "actor-actor",
        "category_subtype": "classify-country",
    },
    {
        "key_name": "states",
        "name": "Estado",
        "plural_name": "Estados",
        "main_collection": "space_time-location",
        "category_subtype": "space_time-state",
    },
    {
        "key_name": "geographicals",
        "name": "Geográficos",
        "plural_name": "Geográficos",
        "main_collection": "space_time-location",
        "category_group": "space_time-state",
        "category_type": "space_time-municipality",
        "category_subtype": "space_time-locality",
    },
    {
        "key_name": "status_projects",
        "name": "Status de Proyecto",
        "plural_name": "Status de Proyectos",
        "main_collection": "project-project",
        "category_subtype": "project-status_project",
    },
]

deprecated_collection_links = []


def send_many_requests():
    import requests
    import json
    import time

    error_ids = [2107]
    # 2075
    all_ids = [
        2107, 2005, 1902, 1896, 1833, 1832, 1737, 1571, 1501,
        1450, 1405, 1270, 797, 760, 718, 49]
    url = "https://ocsa.ibero.mx/api/rpc/approve_draft"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoib2Nzd2ViYWRtaW4iLCJlbWFpbCI6InNlYmFzdGlhbi5vbHZlcmFAaWJlcm8ubXgifQ.boDDaOPQXa9Q3LMohHXQvuw85fR5rEKPcMxr4nqzGms'
    }

    for elem_id in all_ids:
        payload = {'_id': elem_id}
        with requests.Session() as session:
            response = session.post(
                url, headers=headers, data=json.dumps(payload))
            if response.text:
                print(f"elem_id: {elem_id} | response: {response.text}")
        time.sleep(35)


def model_fields():
    from django.apps import apps
    my_model = apps.get_model("source", "Note")
    fields = my_model._meta.get_fields()
    for field in fields:
        try:
            print(field.default)
            print(type(field.default))
        except AttributeError:
            pass

