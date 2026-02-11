<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import GenericDisplay from "~/components/dashboard/common/select/GenericDisplay.vue";
const mainStore = useMainStore()
const { schemas, all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  main_object: {
    type: Object,
    required: true,
  },
  filter_group_name: {
    type: String,
    required: true,
  },
  main_collection: Object,
  main_collection_name: String,
  category_group_value: Number,
  field: String,
  forced_level: String,

  special_multiple: Boolean,
  width: Number,
})

const loaded = ref(false)

const levels = ['group', 'type', 'subtype']

const filter_node = computed(() => all_nodes.value[props.filter_group_name])
const filter_group_data = computed(() => {
  return filter_node.value.data
})

const final_main_collection = computed(() => {
  if (props.main_collection)
    return props.main_collection
  else if (props.main_collection_name)
    return schemas.value.collections_dict[props.main_collection_name]
  return null
})

const is_multiple = computed(() => {
  if (final_main_collection.value){
    if (props.field){
      const field_obj = final_main_collection.value.fields.find(
        field => field.name === props.field)
      if (field_obj){
        if (["many_to_many", "one_to_many"].includes(field_obj.relation_type))
          return true
      }
    }
  }
  return false
})

const category_is_multiple = computed(() => {
  if (props.forced_level === 'subtype')
    return is_multiple.value
  return false
})

const collections = computed(() => {
  return Object.entries(level_names.value).reduce((acc, [level, cat_name]) => {
    acc[level] = schemas.value.collections_dict[cat_name]
    return acc
  }, {})
})

const subcategory_is_multiple = computed(() => {
  if (props.forced_level)
    return false
  if (is_multiple.value)
    return true
  if (props.special_multiple)
    return true
  if (final_main_collection.value){
    const subtype_field = final_main_collection.value.fields.find(field =>
      field.related_snake_name === collections.value.subtype.snake_name)
    return subtype_field && subtype_field.relation_type === 'many_to_many'
  }
  return false
})

const level_names = computed(() => {
  let done = false
  return levels.reduce((acc, level) => {
    if (props.forced_level === level)
      done = true
    if (done)
      return acc
    const cat_name = filter_group_data.value[`category_${level}`]
    if (cat_name)
      acc[level] = cat_name
    return acc
  }, {})
})

function isLevelMultiple(level, cat_name){
  let is_multiple = false
  if (level === 'subtype')
    is_multiple = subcategory_is_multiple.value
  else if (level === 'type')
    is_multiple = category_is_multiple.value
  if (is_multiple)
    cat_name = `${cat_name}s`
  return [is_multiple, cat_name]
}

const level_final_names = computed(() => {
  let final_names = {}
  Object.entries(level_names.value).forEach(([level, cat_name]) => {
    const [is_multiple, new_cat_name] = isLevelMultiple(level, cat_name)
    final_names[level] = new_cat_name
  })
  return final_names
})

const category_values = computed(() => {
  return Object.entries(level_final_names.value).reduce((acc, [level, cat_name]) => {
    let value = props.main_object[cat_name]
    if (!value && level === 'group' && props.category_group_value)
      value = props.category_group_value
    try{
      const is_object = typeof value === 'object' && value !== null
      if (level === 'subtype' && is_object && subcategory_is_multiple.value)
        acc[level] = value[0]
      else if (level === 'type' && is_object && category_is_multiple.value)
        acc[level] = value[0]
      else
        acc[level] = value
    }
    catch (error){
      console.log("error", error)
      console.log("level", level)
      console.log("cat_name", cat_name)
      console.log("main_object", props.main_object)
      console.log("category_group_value", props.category_group_value)
      console.log("value", value)
    }
    return acc
  }, {})
})

function getNode(level='group'){
  if (category_values.value[level])
    return filter_node.value.find(
      d => d.id === `${level}_${category_values.value[level]}`)
  return null
}

const nodes = computed(() => {
  let subtype_node = getNode('subtype')
  let data = {"subtype": subtype_node}
  if (level_names.value.type){
    let type_node = getNode('type')
    if (!type_node){
      type_node = subtype_node
        ? subtype_node.parent
        : null
    }
    data.type = type_node
    if (level_names.value.group){
      let group_node = getNode('group')
      if (!group_node){
        group_node = type_node
          ? type_node.parent
          : subtype_node
            ? subtype_node.parent.parent
            : null
      }
      data.group = group_node
    }
  }
  return data
})

const type_items = computed(() => {
  // console.log("level_group", level_names.value.group)
  if (level_names.value.group){
    // console.log("nodes", nodes.value)
    if (nodes.value.group && nodes.value.group.children)
      return nodes.value.group.children.map(child => child.data)
  }
  else
    return filter_node.value.children.map(child => child.data)
  return []
})

const is_open_search = computed(() => {
  return filter_group_data.value?.open_search || false
})

const subtype_items = computed(() => {
  if (level_names.value.type) {
    if (nodes.value.type && nodes.value.type.children) {
      if (nodes.value.type.data.all_childs)
        return nodes.value.type.data.all_childs
      return nodes.value.type.children.map(child => child.data)
    }
    else if (is_open_search.value){
      const all_subtypes = filter_node.value.leaves().filter(
        leaf => leaf.id.startsWith(`subtype_`))
      return all_subtypes.map(leaf => leaf.data)
    }
    else
      return null
  }
  else{
    // console.log("all_nodes", all_nodes.value)
    // console.log("filter_node", filter_node.value)
    return filter_node.value.children.map(child => child.data)
  }
})

onMounted(() => {
  // TODO: revisar con calma esto:
  const levels = level_names.value
  if (!props.main_object[levels.type] && nodes.value.type)
    props.main_object[levels.type] = nodes.value.type.data.id
  // if (props.main_object[levels.subtype] && !props.main_object[levels.type]){
  //   if (nodes.value.subtype)
  //     props.main_object[levels.type] = nodes.value.subtype.parent.data.id
  // }

})

const type_field = computed(() => {
  if (props.field)
    return props.field
  return level_final_names.value.type
})

const subtype_field = computed(() => {
  if (props.field)
    return props.field
  return level_final_names.value.subtype
})

const display_type = computed(() => {
  if (!level_names.value.type)
    return false
  return props.forced_level
    ? (props.main_object[level_names.value.type] || type_items.value)
    : true
})

nextTick(() => {
  setTimeout(() => {
    setInitialData()
  }, 100)
  setTimeout(() => {
    loaded.value = false
    setInitialData()
  }, 2500)
})

function setInitialData() {
  if (loaded.value)
    return
  loaded.value = true
  if (props.is_filter)
    return
  const levels = level_final_names.value
  if (props.main_object[levels.subtype]
      && !props.main_object[levels.type]){
    if (nodes.value.subtype){
      // console.log("nodes.value.subtype", nodes.value.subtype)
      props.main_object[levels.type] = nodes.value.subtype.parent.data.id
    }
  }
  if (props.main_object[levels.type]
      && !props.main_object[levels.group]){
    if (nodes.value.type)
      props.main_object[levels.group] = nodes.value.type.parent.data.id
  }
}

const subtype_key = computed(() => {
  const fields = collections.value.subtype.fields
  const available_ids = ['id', 'key_name', 'name']
  return available_ids.find(id => fields.some(field => field.name === id))
})

</script>

<template>
  <GenericDisplay
    v-if="collections.group && (forced_level || true)"
    :element_value="main_object[level_names.group]"
    level="group"
    :items="filter_group_data.category_groups"
  />
  <GenericDisplay
    v-if="display_type"
    :element_value="main_object[type_field]"
    level="type"
    :items="type_items"
    :is_multiple="category_is_multiple"
  />
  <GenericDisplay
    v-if="subtype_items && level_names.subtype"
    :element_value="main_object[subtype_field]"
    level="subtype"
    :item_value="subtype_key"
    :items="subtype_items"
    :is_multiple="subcategory_is_multiple"
  />

</template>

<style scoped>

</style>