import {computed, ref} from "vue";

export const status_filters = {
  "register": {
    name: "de Registro",
    hidden: false,
    key_name: "register",
    collection: "status_register",
    collection_group: "status",
    order: 4,
  },
  "validation": {
    name: "de Validación",
    hidden: false,
    key_name: "validation",
    collection: "status_validation",
    collection_group: "status",
    order: 5,
  },
  "location": {
    name: "de Ubicación",
    hidden: true,
    key_name: "location",
    collection: "status_location",
    collection_group: "status",
    order: 6,
  }
}


const all_filters_old = ref([
  {
    name: "Tipo de Extr.", order: 0, init_visible: true,
    key: "extractivism_type", title: "Tipo de Extractivismo",
    collection: "extractivism_types",
    groups: ['project', 'extractivism_type']
  },{
    name: "de Registro", order: 4, init_visible: true,
    collection: "status_register", collection_group: "status",
    groups: ['project']
  },{
    name: "de Ubicación", order: 6, init_visible: false,
    collection: "status_location", disabled: true, collection_group: "status",
    groups: ['project']
  },{
    name: "Medio", order: 1, init_visible: true,
    key: "source", title: "Medio de comunicación",
    collection: "sources",
    groups: ['note']
  },{
    name: "Tipo de participante", order: 2, init_visible: true,
    key: "participant_type", title: "Tipo de participante",
    collection: "participant_types",
    groups: ['actor']
  },{
    name: "Pertenencia", order: 3, init_visible: true,
    key: "belongs", title: "Grupo de pertenencia",
    collection: "belongs", item_id: "key_name",
    groups: ['actor']
  },{
    name: "Redes", order: 4, init_visible: true, key: "network_seq",
    collection: "networks", groups: ['actor']
  },{
    name: "Tipo de MP", order: 1, init_visible: false, is_autocomplete: true,
    key: "megaproject_type", title: "Tipo de Megaproyecto",
    collection: "megaproject_types", groups: ['project'],
  },{
    name: "Estado", order: 6, init_visible: true, key: "state",
    collection: "states", groups: ['project']
  },{
    name: "st-Proyecto", order: 8, init_visible: false,
    title: "Status de proyecto",
    collection: "status_project", groups: ['project']
  },
  // {
  //   name: "Af. social", order: 9, init_visible: true,
  //   key: "social_impact", title: "Afectación social",
  //   collection: "social", collection_group: "impact",
  //   groups: ['project']
  // },
  // {
  //   name: "Af. ambiental", order: 10, init_visible: true,
  //   key: "environment_impact", title: "Afectación ambiental",
  //   collection: "environmental", collection_group: "impact",
  //   groups: ['project']
  // },
  // {
  //   name: "Tipo de Evento", order: 11, init_visible: false,
  //   key: "event_type", collection: "event_types",
  //   groups: ['project', 'event']
  // }
])


// const group_filters = computed(() => {

const common_sorts = {
  'name': 'Nombre',
  'status_validation__order': 'Status de Validación',
  'status_register__order': 'Status de Registro',
  'status_location__order': 'Status de Ubicación',
  'count': 'Cantidad',
  'id': 'Fecha de creación',
}

export const final_sorts = computed(() => {
  return []
  // if (!group.value.sorts && !group.value.same_sorts)
  //   return []
  // let same_sorts = {}
  // if (group.value.same_sorts)
  //   same_sorts = group.value.same_sorts.reduce((coll, sort) =>(
  //     {...coll, [sort]: common_sorts[sort]}
  //   ), {})
  // console.log("same_sorts", same_sorts)
  // let joined_sorts = {...same_sorts, ...(group.value.sorts || {})}
  // return Object.entries(joined_sorts).map(([key, value]) => {
  //   console.log("key", key, "value", value)
  //   return {value: key, title: value}
  // })
})

