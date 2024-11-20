<script setup>

import {computed, nextTick} from "vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
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
  is_filter: Boolean,
  is_toolbar: Boolean,
  main_collection: Object,
  category_group_value: Number,
  forced_level: String,
  field: String,
  width: Number,
})

const emits = defineEmits(['delete-record'])
const levels = ['group', 'type', 'subtype']

const filter_node = computed(() => all_nodes.value[props.filter_group_name])
const filter_group = computed(() => filter_node.value.data)

const subcategory_is_multiple = computed(() => {
  if (props.main_collection){
    if (props.field){
      const field_obj = props.main_collection.fields.find(
        field => field.name === props.field)
      if (field_obj){
        if (["many_to_many", "one_to_many"].includes(field_obj.relation_type))
          return true
      }
    }
    const category = props.main_collection.categories.find(
      cat => cat.parent === filter_group.value.category_subtype) || {}
    return category.is_multiple || false
  }
  return false
})

const level_names = computed(() => {
  let done = false
  return levels.reduce((acc, level) => {
    if (done)
      return acc
    if (props.forced_level === level){
      done = true
      return acc
    }
    const cat_name = filter_group.value[`category_${level}`]
    if (cat_name)
      acc[level] = cat_name
    return acc
  }, {})
})

const collections = computed(() => {
  return Object.entries(level_names.value).reduce((acc, [level, cat_name]) => {
    acc[level] = schemas.value.collections_dict[cat_name]
    return acc
  }, {})
})

const category_values = computed(() => {
  return Object.entries(level_names.value).reduce((acc, [level, cat_name]) => {
    if (level === 'subtype' && subcategory_is_multiple.value)
      cat_name = `${cat_name}s`
    let value = props.main_object[cat_name]
    if (!value && level === 'group' && props.category_group_value)
      value = props.category_group_value
    if (level === 'subtype' && typeof value === 'object' && subcategory_is_multiple.value)
      acc[level] = value[0]
    else
      acc[level] = value
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

const group_object = computed(() => {
  return nodes.value.group
    ? nodes.value.group.data
    : {name: "Todos", color: "primary", icon: "category"}
})

const type_items = computed(() => {
  if (level_names.value.group){
    if (nodes.value.group && nodes.value.group.children)
      return nodes.value.group.children.map(child => child.data)
  }
  else
    return filter_node.value.children.map(child => child.data)
  return []
})

const subtype_items = computed(() => {
  if (level_names.value.type) {
    if (nodes.value.type && nodes.value.type.children) {
      if (nodes.value.type.data.all_childs)
        return nodes.value.type.data.all_childs
      return nodes.value.type.children.map(child => child.data)
    }
  }
  else
    return filter_node.value.children.map(child => child.data)
  return null
})

onMounted(() => {
  if (!props.main_object[level_names.value.type] && nodes.value.type)
    props.main_object[level_names.value.type] = nodes.value.type.data.id
})

const subtype_field = computed(() => {
  if (props.field)
    return props.field
  return subcategory_is_multiple.value
    ? `${level_names.value.subtype}s`
    : level_names.value.subtype
})

const type_label = computed(() => {
  // console.log("collections", collections.value)
  // console.log("filter_node", filter_node.value)
  if (!collections.value.type)
    return "??"
  if (props.is_filter && group_object.value && level_names.value.group)
    return `${collections.value.type.name} ${group_object.value.name}`
  return collections.value.type.name
})

const display_type = computed(() => {
  // v-if="level_names.type && (forced_level ? (main_object[level_names.type] || type_items) : true)"
  if (!level_names.value.type)
    return false
  return props.forced_level
    ? (props.main_object[level_names.value.type] || type_items.value)
    : true
})
const display_indirect_type = computed(() => {
  if (props.is_filter)
    return false
  return props.main_object[level_names.value.type] === undefined
})


nextTick(() => {
  setTimeout(() => {
    if (props.is_filter || props.is_toolbar)
      return
    if (props.main_object[level_names.value.subtype]
        && !props.main_object[level_names.value.type]){
      if (nodes.value.subtype)
        props.main_object[level_names.value.type] = nodes.value.subtype.parent.data.id
    }
  }, 10)
})

const subtype_key = computed(() => {
  const fields = collections.value.subtype.fields
  const available_ids = ['id', 'key_name', 'name']
  return available_ids.find(id => fields.some(field => field.name === id))
})

const main_width = computed(() => props.width || 250)


</script>

<template>
  <template v-if="is_toolbar">
    <v-col cols="12" class="d-flex px-0 pt-1">
      <v-btn
        @click="emits('delete-record')"
        icon="delete"
        color="error"
        variant="text"
        class="mr-2 mt-n2 ml-n2"
      >
      </v-btn>
      <slot name="chip">
        <div
          v-if="collections.group && is_toolbar"
          class="d-flex mr-2 flex-column"
        >
          <v-chip
            class="mr-1"
            :color="group_object.color"
            min-width="150"
            :prepend-icon="group_object.icon"
          >
            {{ group_object.name }}
          </v-chip>
  <!--        <v-btn-->
  <!--          size="x-small"-->
  <!--          color="error"-->
  <!--          variant="outlined"-->
  <!--          class="mt-1"-->
  <!--          @click="emits('delete-record')"-->
  <!--        >-->
  <!--          Eliminar-->
  <!--        </v-btn>-->
        </div>
        <v-chip v-else variant="outlined" color="grey" min-width="150" label>
          {{ main_collection.name }}
        </v-chip>
      </slot>

    </v-col>
  </template>
  <div v-else-if="collections.group && forced_level">
    <v-select
      v-model="main_object[level_names.group]"
      :items="filter_group.category_groups"
      item-title="name"
      item-value="id"
      :label="collections.group.name"
      :variant="is_filter ? 'underlined' : 'outlined'"
      :clearable="is_filter"
      class="ml-2"
      :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
    >
    </v-select>
  </div>
  <template v-if="display_type">
<!--    <div-->
<!--      v-if="display_indirect_type"-->
<!--    >-->
<!--      Hola mundo {{subtype_object}}-->
<!--    </div>-->

<!--      v-else-->
    <v-select
      v-model="main_object[level_names.type]"
      :items="type_items"
      item-title="name"
      item-value="id"
      :label="type_label"
      _density="density"
      :variant="is_filter ? 'underlined' : 'outlined'"
      :clearable="is_filter"
      class="ml-2"
      :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
    >
<!--    <template #item="{ item, props: {onClick, title, value} }" v-if="true">-->
<!--      <v-list-item-->
<!--        @click="onClick"-->
<!--      >-->
<!--        <v-list-item-title>-->
<!--          <b class="mr-1"> {{ item.title }} </b>-->
<!--          <span v-if="item.raw.has_subtype">-->
<!--            (tiene subtipos)-->
<!--          </span>-->
<!--        </v-list-item-title>-->
<!--        <v-list-item-subtitle>-->
<!--          {{ item.raw.description }}-->
<!--        </v-list-item-subtitle>-->
<!--      </v-list-item>-->
<!--    </template>-->
    </v-select>
  </template>


  <v-select
    v-if="subtype_items && level_names.subtype"
    v-model="main_object[subtype_field]"
    :items="subtype_items"
    item-title="name"
    :item-value="subtype_key"
    :label="collections.subtype[subcategory_is_multiple ? 'plural_name' : 'name']"
    _density="density"
    :variant="is_filter ? 'underlined' : 'outlined'"
    :clearable="is_filter"
    :multiple="subcategory_is_multiple"
    class="ml-2"
    :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
  >
<!--    <template #item="{ item, props: {onClick, title, value} }">-->
<!--      <v-list-item-->
<!--        @click="onClick"-->
<!--        :title="title"-->
<!--        :subtitle="item.raw.description"-->
<!--      >-->
<!--      </v-list-item>-->
<!--    </template>-->

  </v-select>

</template>

<style scoped>

</style>