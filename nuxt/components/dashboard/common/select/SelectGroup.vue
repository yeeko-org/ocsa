<script setup>

import {computed, nextTick} from "vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
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
  category_group_value: Number,
  main_collection: Object,
  main_collection_name: String,
  field: String,
  forced_level: String,

  is_filter: Boolean,
  is_toolbar: Boolean,
  width: Number,
  subtype_class: String,
  is_display: Boolean,
  required: Boolean,
})

const collection_display = ref(null)
const loaded = ref(false)
const dialog_add = ref(false)
const main_action = ref("click")
const level_dialog = ref(null)
const init_filters = ref(null)
const init_in_edition = ref(null)

const emits = defineEmits(['delete-record'])
const levels = ['group', 'type', 'subtype']

const filter_node = computed(() => all_nodes.value[props.filter_group_name])
const filter_group_data = computed(() => {
  // console.log("filter_node", filter_node.value)
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

const subcategory_is_multiple = computed(() => {
  if (is_multiple.value)
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
    if (!done){
      const cat_name = filter_group_data.value[`category_${level}`]
      if (cat_name)
        acc[level] = cat_name
    }
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
    if (level === 'type' && category_is_multiple.value)
      cat_name = `${cat_name}s`
    let value = props.main_object[cat_name]
    if (!value && level === 'group' && props.category_group_value)
      value = props.category_group_value
    if (level === 'subtype' && typeof value === 'object' && subcategory_is_multiple.value)
      acc[level] = value[0]
    else if (level === 'type' && typeof value === 'object' && category_is_multiple.value){
      acc[level] = value[0]
    }
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

const subtype_items = computed(() => {
  if (level_names.value.type) {
    if (nodes.value.type && nodes.value.type.children) {
      if (nodes.value.type.data.all_childs)
        return nodes.value.type.data.all_childs
      return nodes.value.type.children.map(child => child.data)
    }
    else
      return null
  }
  else
    return filter_node.value.children.map(child => child.data)
})

onMounted(() => {
  // TODO: revisar con calma esto:
  if (!props.main_object[level_names.value.type] && nodes.value.type)
    props.main_object[level_names.value.type] = nodes.value.type.data.id
})

const type_field = computed(() => {
  if (props.field)
    return props.field
  return category_is_multiple.value
    ? `${level_names.value.type}s`
    : level_names.value.type
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

nextTick(() => {
  setTimeout(() => {
    setInitialData()
  }, 100)
})

function setInitialData(){
  if (loaded.value)
    return
  loaded.value = true
  // if (props.is_filter || props.is_toolbar)
  if (props.is_filter)
    return
  if (props.main_object[level_names.value.subtype]
      && !props.main_object[level_names.value.type]){
    if (nodes.value.subtype)
      props.main_object[level_names.value.type] = nodes.value.subtype.parent.data.id
  }
  if (props.main_object[level_names.value.type]
      && !props.main_object[level_names.value.group]){
    if (nodes.value.type)
      props.main_object[level_names.value.group] = nodes.value.type.parent.data.id
  }
}

const subtype_key = computed(() => {
  const fields = collections.value.subtype.fields
  const available_ids = ['id', 'key_name', 'name']
  return available_ids.find(id => fields.some(field => field.name === id))
})

const main_width = computed(() => props.width || 250)

function openDialog(level_name, is_add=true){
  level_dialog.value = level_name
  let done = false
  init_filters.value = Object.entries(level_names.value).reduce((acc, [level, cat_name]) => {
    // console.log("level", level)
    const [is_multiple, new_cat_name] = isLevelMultiple(level, cat_name)
    if (level === level_name)
      done = true
    if (!done){
      let new_value = props.main_object[new_cat_name]
      if (is_multiple && new_value.length)
        new_value = new_value[0]
      acc[cat_name] = new_value
    }
    return acc
  }, {})
  let real_value = null
  if (level_name === 'group')
    real_value = props.main_object[level_names.value['group']]
  else if (level_name === 'type')
    real_value = props.main_object[type_field.value]
  else if (level_name === 'subtype')
    real_value = props.main_object[subtype_field.value]
  if (real_value){
    if (typeof real_value === 'object')
      init_in_edition.value = real_value
    else
      init_in_edition.value = [real_value]
  }
  else
    init_in_edition.value = null
  main_action.value = is_add ? "click" : "checkbox"
  dialog_add.value = true
  nextTick(() => {
    collection_display.value.changeInitFilters()
  })
}

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


function selectItem(item){
  // console.log("item", item)
  // console.log("level_dialog", level_dialog.value)
  // console.log("level_names", level_names.value)
  // console.log("main_object", props.main_object)
  const elem_id = item.id || item.key_nme
  Object.entries(level_names.value).forEach(([level, cat_name]) => {
    const [is_multiple, new_cat_name] = isLevelMultiple(level, cat_name)
    if (level === level_dialog.value)
      props.main_object[new_cat_name] = is_multiple
        ? [elem_id]
        : elem_id
    else
      props.main_object[new_cat_name] = is_multiple
        ? []
        : null
  })
  loaded.value = false
  setInitialData()
  // console.log("main_object", props.main_object)
  // console.log("main_node", all_nodes.value[props.filter_group_name])
  dialog_add.value = false
}

function changeValue(level_name, value){
  if (level_name === 'group')
    props.main_object[type_field.value] = null
  props.main_object[subtype_field.value] = null
}


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
          {{ final_main_collection.name }}
        </v-chip>
      </slot>
    </v-col>
  </template>
  <GenericSelect
    v-else-if="collections.group && forced_level"
    :main_object="main_object"
    level="group"
    :level_name="level_names.group"
    :is_filter="is_filter"
    :main_width="width || 200"
    :items="filter_group_data.category_groups"
    :label="collections.group.name"
    :class="{'mr-2': !is_display}"
    :is_display="is_display"
    :required="required"
    @update-value="changeValue('group', $event)"
  />
  <GenericSelect
    v-if="display_type"
    :main_object="main_object"
    level="type"
    :level_name="type_field"
    :is_filter="is_filter"
    :main_width="main_width"
    :items="type_items"
    :label="type_label"
    :is_display="is_display"
    :is_multiple="category_is_multiple"
    :class="{'mr-2': !is_display}"
    :required="required"
    :collection_data="collections.type"
    @open-dialog="openDialog('type', $event)"
    @update-value="changeValue('type', $event)"
  />
  <GenericSelect
    v-if="subtype_items && level_names.subtype"
    :main_object="main_object"
    level="subtype"
    :level_name="subtype_field"
    :is_filter="is_filter"
    :main_width="main_width"
    :item_value="subtype_key"
    :items="subtype_items"
    :is_display="is_display"
    :class="subtype_class"
    :is_multiple="subcategory_is_multiple"
    :label="collections.subtype[subcategory_is_multiple ? 'plural_name' : 'name']"
    :required="required"
    :collection_data="collections.subtype"
    @open-dialog="openDialog('subtype', $event)"
  />
  <v-dialog
    v-model="dialog_add"
    max-width="1020"
  >
    <v-card>
      <v-card-title class="text-h5 d-flex">
        {{ collections[level_dialog].plural_name }}
        <v-spacer></v-spacer>
        <v-btn
          icon
          @click="dialog_add = false"
          variant="text"
        >
          <v-icon>close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text class="py-0">
        <v-alert
          v-if="main_action === 'click'"
          type="info"
          variant="outlined"
        >
          Antes de agregar un nuevo registro, explora las categorías disponibles
        </v-alert>
        <CollectionDisplay
          ref="collection_display"
          :parent_collection="collections[level_dialog]"
          @select-item="selectItem"
          :main_action="main_action"
          :init_filters="init_filters"
          :init_in_edition="init_in_edition"
        />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>