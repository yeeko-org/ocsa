
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
    edit: "NoteEdit",
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
    edit: "ProjectEdit",
    key: 'project',
    // icon: 'corporate_fare'},
    // icon: 'flood'},
    // icon: 'stadium'},
    // icon: 'real_estate_agent'},
    // icon: 'holiday_village'},
    // icon: 'engineering'},
    icon: 'factory',
    color: 'purple',
    // 'id', 'name', 'mentions_count'
    same_sorts: [
      'id', 'status_register__order', 'name', 'status_location__order'],
    catalogs: [
      {
        name: 'Tipos de extractivismo',
        key: 'extractivism_type',
        singular: 'tipo de extractivismo',
        header: "MegaProjectTypeHeader",
        sheet: "MegaProjectTypeSheet",
        edit: "MegaProjectTypeEdit",
        meta_key: 'project',
        simplified_filters: true,
        sorts: {'count': 'Cantidad de proyectos'},
        same_sorts: ['status_validation__order', 'count'],
      },
      {name: 'Estados de proyectos', key: 'status_project',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Afectaciones sociales', key: 'social_impact',
        icon: 'groups', color: 'teal',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Afectaciones ambientales', key: 'environment_impact',
        icon: 'eco', color: 'green',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      // {
      //   name: 'Subafectaciones',
      //   key: 'impact_subtype',
      //   icon: 'groups',
      //   color: 'teal',
      //   header: "HeaderGeneric",
      //   sheet: "SheetCommon",
      //   header: "SubImpactHeader",
      //   sheet: "SubImpactSheet",
      //   edit: "SubImpactEdit",
      //   meta_key: 'generic',
      //   simplified_filters: true,
      //   sorts: {'count': 'Cantidad de proyectos'},
      // },
    ],
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
    sorts: {'mentions_count': 'Cantidad de menciones'},
    same_sorts: ['status_validation__order', 'name'],
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
    simplified_filters: true,
    catalogs: [
      {name: 'Tipos de eventos', key: 'event_type',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
      {name: 'Roles en las acciones', key: 'involved_role',
        header: "HeaderGeneric", sheet: "SheetCommon", meta_key: 'generic'},
    ]
  },
]
