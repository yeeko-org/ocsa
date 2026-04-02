import {status_filters} from "~/composables/filters.js";

// const calculateSchemas = (data) => {
export function calculateSchemas(data) {
  let filter_groups = data.filter_groups.map(fg => {
    return {...fg, ...fg.addl_config}
  })
  const filters_dict = filter_groups.reduce((obj, fg) => {
    obj[fg.key_name] = fg
    return obj
  }, {})
  const has_fields = [
    "comments", "description", "help_text", "order", "color", "icon"]
  // const name_fields = ["name", "title", "description"]
  const name_fields = ["name", "title"]
  let collections_dict = data.collections.reduce((obj, coll) => {
    coll.catalog_groups = filter_groups.reduce((arr, new_fg) => {
      if (new_fg.main_collection !== coll.snake_name)
        return arr
      const cat_group = new_fg.category_group || new_fg.special_group
      if (cat_group)
        new_fg.category_groups = data[cat_group] || []
      return [...arr, new_fg]
    }, [])
    const valid_relations = ['one_to_many', 'many_to_many']
    coll.child_relation_fields = coll.fields.filter(field => {
      return valid_relations.includes(field.relation_type)
    })
    const primary_key = coll.fields.find(f => f.primary_key)
    coll.pk = primary_key ? primary_key.name : 'id'
    name_fields.forEach(field => {
      if (coll.name_field)
        return
      if (coll.fields.some(f => f.name === field))
        coll.name_field = field
    })
    coll.has = has_fields.reduce((obj, field) => {
      obj[field] = coll.fields.some(f => f.name === field)
      return obj
    }, {})
    const other_fields = has_fields.concat([coll.pk, coll.name_field])
    coll.other_fields = coll.fields.filter(f =>
      !other_fields.includes(f.name) && f.relation_type === 'simple')

    const all_filters = coll.all_filters || []

    let available_sorts = [
      {
        title: "Más recientes",
        value: "-id"
      },
      {
        title: "Más antiguos",
        value: "id"
      },
    ]

    let collection_filters = all_filters.reduce((arr, filter) => {
      if (!filter.filter_name){
        arr.push({...filter, order: 12, is_custom: true})
        return arr
      }
      const filter_data = filters_dict[filter.filter_name]
      if (!filter_data){
        console.error("No filter data", filter.filter_name)
        return arr
      }
      const new_filter = {...filter_data, ...filter}
      arr.push(new_filter)
      return arr
    }, [])
    coll.is_category = coll.level.includes('category_')
    if (coll.is_category){
      const fg = filter_groups.find(fg => fg[coll.level] === coll.snake_name)
      // const fg = filters_dict[coll.snake_name]
      if (fg){
        coll.filter_group = fg
        const short_level = coll.level.replace('category_', '')
        const new_filter_group = {
          ...fg,
          short_name: `${fg.short_prev} ${fg.name}`,
          name: `${fg.prev} ${fg.name}`,
          forced_level: short_level,
          order: 1,
        }
        collection_filters.push(new_filter_group)
      }
    }

    const status_groups = coll.fields.reduce((arr, field)=>{
      if (field.related_model === 'StatusControl')
        arr.push(field.name)
      return arr
    }, [])
    coll.status_groups = status_groups
    status_groups.forEach(sg => {
      const status = status_filters[sg]
      collection_filters.push(status)
      available_sorts.push({
        value: `${status.collection}__order`,
        title: `Status ${status.name}`
      })
    })
    if (coll.name_field)
      available_sorts.push({
        title: "Nombre / Título",
        value: coll.name_field
      })
    if (coll.has.order)
      available_sorts.push({
        title: "Orden",
        value: "order"
      })
    collection_filters = collection_filters.sort((a, b) => a.order - b.order)

    coll.collection_filters = collection_filters
    coll.available_sorts = available_sorts

    obj[coll.snake_name] = {...coll.cat_params || {}, ...coll}
    return obj
  }, {})
  return {
    // "collections": collections,
    "collections_dict": collections_dict,
    "filter_groups": filter_groups,
    "filters_dict": filters_dict,
  }
}