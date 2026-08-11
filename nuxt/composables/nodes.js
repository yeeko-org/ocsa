import * as d3 from "d3";

export function hydrateFilterGroup(fg, data, collections_dict) {
  const group_key = fg.category_group
  const type_key = fg.category_type
  const subtype_key = fg.category_subtype
  let subtypes = data[subtype_key] || []
  let types = data[type_key] || []
  let groups = data[group_key] || []

  const subtype_collection = collections_dict[subtype_key]
  if (!subtype_collection){

    console.log("filter_group", fg)
    console.log("subtype_collection", subtype_collection)
    console.log("subtype_key", subtype_key)
    console.log("collections_dict", collections_dict)

  }
  let type_field = subtype_collection.fields.find(field =>
    field.related_snake_name === fg.category_type)
  if (type_field)
    type_field.is_multiple = type_field.relation_type === 'many_to_many'

  let root = {
    new_id: "root",
    parent: null,
    name: "root",
  }
  root = {...root, ...fg}
  let new_types = []
  let types_dict = {}
  const first_group = groups[0]
  if (type_key){
    const some_is_empty = subtypes.some(st => {
      const type_value = st[type_field.name]
      if (Array.isArray(type_value))
        return !type_value.length
      return !type_value
    })
    if (some_is_empty){
      let new_type ={
        id: 0,
        new_id: "type_0",
        name: 'Desconocido ⚠️',
        original_types: null,
        color: "red",
        icon: "error_outline",
        is_mix: true,
      }
      if (group_key)
        new_type[group_key] = first_group.id
      new_types.push(new_type)
    }
  }

  subtypes = subtypes.map(st => {
    if (type_field && type_field.is_multiple){
      let all_types = st[type_field.name]
      all_types.forEach(t => {
        if (!types_dict[t])
          types_dict[t] = []
        types_dict[t].push(st)
      })
      if (all_types.length === 1)
        st.parent_id = `type_${all_types[0]}`
      else if (!all_types.length){
        st.parent_id = "type_0"
        // console.log("No first type", st)
      }
      else{
        let new_type_key = ''
        const join_id = all_types.join('_')
        const names = all_types.map(t =>
          types.find(tt => tt.id === t).name)
        if (group_key){
          const first_type = types.find(t => t.id === all_types[0])
          new_type_key = first_type[group_key]
        }
        st.parent_id = `type_${join_id}`
        if (!new_types.find(t => t.id === join_id)){
          let new_type = {
            id: join_id,
            name: `Mixto: ${names.join(', ')}`,
            original_types: all_types.map(t =>
              types.find(tt => tt.id === t)),
            new_id: `type_${join_id}`,
            color: "black",
            icon: "group_work",
            is_mix: true,
          }
          if (group_key)
            new_type[group_key] = new_type_key
          new_types.push(new_type)
        }
      }
    }
    else if (type_key)
      st.parent_id = `type_${st[type_field.name]}`
    else
      st.parent_id = "root"
    st.new_id = `subtype_${st.id}`
    return st
  })
  types = [...types, ...new_types]
  types = types.map(type => {
    if (group_key && !type[group_key]) {
      console.log("No group key", type)
    }
    type.parent_id = group_key ? `group_${type[group_key]}` : "root"
    type.new_id = `type_${type.id}`
    if (type_field.is_multiple)
      type.all_childs = types_dict[type.id]
    return type
  })
  groups = groups.map(g => {
    g.parent_id = "root"
    g.new_id = `group_${g.id}`
    return g
  })
  const all_data = [...subtypes, ...types, ...groups, root]

  try{
    return d3.stratify()
      .id(d => d.new_id)
      .parentId(d => d.parent_id)
      (all_data)
  }
  catch (e){
    console.log("Error", e)
    console.log("all_data", all_data)
    console.log("subtype_key", subtype_key)
    console.log("type_key", type_key)
    console.log("group_key", group_key)

    console.log("subtypes", subtypes)
    console.log("types", types)
    console.log("groups", groups)
    return null
  }
}

// const calculateNewCats = (data, schemas) => {
export function calculateNewCats(data, schemas) {
  let all_nodes = {}
  schemas.filter_groups.forEach(fg => {
    const hydrated_filter_group = hydrateFilterGroup(
      fg, data, schemas.collections_dict)
    if (hydrated_filter_group)
      all_nodes[fg.key_name] = hydrated_filter_group
  })
  return all_nodes
}
