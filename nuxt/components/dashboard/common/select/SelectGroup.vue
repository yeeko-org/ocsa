<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";

const mainStore = useMainStore()
const { schemas, all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  filter_group_name: {
    type: String,
    required: true,
  },
  main_collection: Object,
  main_collection_name: String,
  category_group_value: Number,
  field: String,
  forced_level: String,

  is_filter: Boolean,
  is_toolbar: Boolean,
  special_multiple: Boolean,
  width: Number,
  subtype_class: String,
  required: Boolean,
  forced_clearable: Boolean,

})
const main_object = defineModel({type: Object, required: true})

const collection_display = ref(null)
const loading = ref(false)
const dialog_add = ref(false)
const main_action = ref("click")
const level_dialog = ref(null)
const init_filters = ref(null)
const init_in_edition = ref(null)

defineExpose({ externalSetInitialData })

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

const levels = ['group', 'type', 'subtype']
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
    let value = main_object.value[cat_name]
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
      console.log("main_object", main_object.value)
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

const is_open_search = computed(() => {
  return filter_group_data.value?.open_search || false
})

const is_autocomplete = computed(() => {
  return filter_group_data.value?.subtype_is_autocomplete || false
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
  if (!main_object.value[levels.type] && nodes.value.type)
    main_object.value[levels.type] = nodes.value.type.data.id
  // if (main_object.value[levels.subtype] && !main_object.value[levels.type]){
  //   if (nodes.value.subtype)
  //     main_object.value[levels.type] = nodes.value.subtype.parent.data.id
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
  // v-if="level_names.type && (forced_level ? (
  // main_object[level_names.type] || type_items) : true)"
  if (!level_names.value.type)
    return false
  return props.forced_level
    ? (main_object.value[level_names.value.type] || type_items.value)
    : true
})

const type_required = computed(() => {
  if (subtype_items.value && level_names.value.subtype)
    return false
  return props.required
})

nextTick(() => {
  setTimeout(() => {
    setInitialData()
  }, 100)
  setTimeout(() => {
    loading.value = false
    setInitialData()
  }, 2500)
})

function externalSetInitialData(){

  nextTick(() => {
    setTimeout(() => {
      loading.value = false
      setInitialData()
    }, 1500)
  })

}

function setInitialData() {
  if (loading.value)
    return
  loading.value = true
  if (props.is_filter)
    return
  const levels = level_final_names.value
  if (main_object.value[levels.subtype]
      && !main_object.value[levels.type]){
    if (nodes.value.subtype){
      // console.log("nodes.value.subtype", nodes.value.subtype)
      main_object.value[levels.type] = nodes.value.subtype.parent.data.id
    }
  }
  if (main_object.value[levels.type]
      && !main_object.value[levels.group]){
    if (nodes.value.type)
      main_object.value[levels.group] = nodes.value.type.parent.data.id
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
  init_filters.value = Object.entries(level_names.value)
    .reduce((acc, [level, cat_name]) => {
      // console.log("level", level)
      const [is_multiple, new_cat_name] = isLevelMultiple(level, cat_name)
      if (level === level_name)
        done = true
      if (!done){
        let new_value = main_object.value[new_cat_name]
        if (is_multiple && new_value.length)
          new_value = new_value[0]
        acc[cat_name] = new_value
      }
      return acc
    }, {})
  let real_value = null
  if (level_name === 'group')
    real_value = main_object.value[level_names.value['group']]
  else if (level_name === 'type')
    real_value = main_object.value[type_field.value]
  else if (level_name === 'subtype')
    real_value = main_object.value[subtype_field.value]
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

function selectItem(item){
  // console.log("item", item)
  // console.log("level_dialog", level_dialog.value)
  // console.log("level_names", level_names.value)
  // console.log("main_object", main_object.value)
  const elem_id = item.id || item.key_name
  Object.entries(level_names.value).forEach(([level, cat_name]) => {
    const [is_multiple, new_cat_name] = isLevelMultiple(level, cat_name)
    if (level === level_dialog.value)
      main_object.value[new_cat_name] = is_multiple
        ? [elem_id]
        : elem_id
    else
      main_object.value[new_cat_name] = is_multiple
        ? []
        : null
  })
  loading.value = false
  setInitialData()
  // console.log("main_object", main_object.value)
  // console.log("main_node", all_nodes.value[props.filter_group_name])
  dialog_add.value = false
}

function changeValue(level_name, value){
  if (level_name === 'group'){
    main_object.value[type_field.value] = null
  }
  main_object.value[subtype_field.value] = null
  main_object.value[level_names.value[level_name]] = value
}

// const emits = defineEmits(['touched'])

function changeSubtypeValue(value){
  // console.log("changeSubtypeValue", value)
  // emits('touched')
  if (filter_group_data.value?.open_search){
    // console.log("loading.value", loading.value)
    loading.value = false
    setInitialData()
  }
}


</script>

<template>
  <template v-if="is_toolbar">
    <v-col cols="12" class="d-flex align-start px-0 pt-1">
      <slot name="chip">
        <v-chip
          v-if="collections.group"
          class="mr-3"
          :color="group_object.color"
          min-width="150"
          :prepend-icon="group_object.icon"
        >
          {{ group_object.name }}
        </v-chip>
        <v-chip v-else variant="outlined" color="grey" min-width="150" label>
          {{ final_main_collection.name }}
        </v-chip>
      </slot>
      <v-spacer></v-spacer>
      <slot name="actions">
      </slot>
    </v-col>
  </template>
  <GenericSelect
    v-else-if="collections.group && (forced_level || true)"
    v-model="main_object"
    :level_name="level_names.group"
    :is_filter="is_filter"
    :main_width="width || 200"
    :items="filter_group_data.category_groups"
    :label="collections.group.name"
    class="mr-2"
    :required="required"
    :forced_clearable="forced_clearable"
    @update-value="changeValue('group', $event)"
  />
  <GenericSelect
    v-if="display_type"
    v-model="main_object"
    :level_name="type_field"
    :is_filter="is_filter"
    :main_width="main_width"
    :items="type_items"
    :label="type_label"
    :is_multiple="category_is_multiple"
    class="mr-2"
    :required="type_required"
    :collection_data="collections.type"
    :forced_clearable="forced_clearable || is_open_search"
    @open-dialog="openDialog('type', $event)"
    @update-value="changeValue('type', $event)"
  />
  <GenericSelect
    v-if="subtype_items && level_names.subtype"
    v-model="main_object"
    :level_name="subtype_field"
    :is_filter="is_filter"
    :main_width="main_width"
    :item_value="subtype_key"
    :items="subtype_items"
    :class="subtype_class"
    :is_multiple="subcategory_is_multiple"
    :label="collections.subtype[subcategory_is_multiple
      ? 'plural_name' : 'name']"
    :required="required"
    :forced_clearable="forced_clearable"
    :collection_data="collections.subtype"
    :is_autocomplete="is_autocomplete"
    @open-dialog="openDialog('subtype', $event)"
    @update-value="changeSubtypeValue($event)"
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