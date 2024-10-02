
// export const menu_old = [
//   {name: "Notas", key: "note", color: 'deep-purple', icon: 'newspaper'},
//   {name: "Proyectos", key: "project", color: 'purple', icon: 'factory'},
//   {name: "Actores", key: "actor", color: 'blue', icon: 'people'},
//   {name: "Eventos", key: "event", color: 'light-blue', icon: 'notifications_active'},
// ]


export const menu_content = [
  {
    name: 'Notas',
    singular: 'nota',
    header: "NoteHeader",
    sheet: "NoteSheet",
    key: 'note',
    color: 'deep-purple',
    icon: 'newspaper',
    catalogs: [
      {name: 'Medios (Fuentes)', key: 'source',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
    ]
  },
  {
    name: 'Proyectos',
    singular: 'proyecto',
    header: "ProjectHeader",
    sheet: "ProjectSheet",
    key: 'project',
    // icon: 'corporate_fare'},
    // icon: 'flood'},
    // icon: 'stadium'},
    // icon: 'real_estate_agent'},
    // icon: 'holiday_village'},
    // icon: 'engineering'},
    icon: 'factory',
    color: 'purple',
    catalogs: [
      {
        name: 'Tipos de extractivismo',
        key: 'extractivism_type',
        singular: 'tipo de extractivismo',
        header: "MegaProjectTypeHeader",
        sheet: "MegaProjectTypeSheet",
        edit: "MegaProjectTypeEdit",
        meta_key: 'project',
      },
      {name: 'Estados de proyectos', key: 'status_project',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Escalas', key: 'project_type',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Afectaciones sociales', key: 'social_impact',
        icon: 'groups', color: 'teal',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Afectaciones ambientales', key: 'environment_impact',
        icon: 'eco', color: 'green',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
    ]

  },
  {
    name: 'Conflictos',
    singular: 'conflicto',
    key: 'conflict',
    icon: 'local_fire_department',
    color: 'lime',
    header: "HeaderGeneric",
    sheet: "SheetCommon",
    meta_key: 'generic',
  },
  {
    name: 'Actores',
    singular: 'actor',
    header: "ActorHeader",
    sheet: "ActorSheet",
    key: 'actor',
    // icon: 'account_balance'
    icon: 'recent_actors',
    color: 'blue',
    catalogs: [
      {name: 'Sectores', key: 'sector',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Grupos de pertenencia', key: 'group',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Tipo de participación', key: 'participation_type',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Grupo de interés', key: 'interest_group',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
    ]
  },
  {
    name: 'Eventos',
    singular: 'evento',
    header: "EventHeader",
    key: 'event',
    // icon: 'work_history'
    icon: 'notifications_active',
    color: 'light-blue',
    catalogs: [
      {name: 'Tipos de eventos', key: 'event_type',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Roles en los eventos', key: 'event_role',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
    ]
  },
]
