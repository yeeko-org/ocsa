<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import GenericSelect from "~/components/dashboard/common/select/GenericSelect.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";

const mainStore = useMainStore()
const { schemas, cats } = storeToRefs(mainStore)

const props = defineProps({
  filter_collection_name: {
    type: String,
    required: true,
  },
  main_collection: Object,
  main_collection_name: String,
  field: String,
  is_filter: Boolean,
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
const init_in_edition = ref(null)

const subtype_items = computed(() => {
  return cats.value[props.filter_collection_name] || []
})

const filter_collection = computed(() => {
  return schemas.value.collections_dict[props.filter_collection_name]
})

const final_main_collection = computed(() => {
  if (props.main_collection)
    return props.main_collection
  else if (props.main_collection_name)
    return schemas.value.collections_dict[props.main_collection_name]
  return null
})

const final_field_object = computed(() => {
  if (props.field){
    return final_main_collection.value.fields.find(
      field => field.name === props.field)
  }
  if (final_main_collection.value){
    return final_main_collection.value.fields.find(field =>
      field.related_snake_name === filter_collection.value.snake_name)
  }
  return null
})

const is_multiple = computed(() => {
  if (!final_field_object.value) return false
  return ["many_to_many", "one_to_many"].includes(
    final_field_object.value.relation_type)
})

const subcategory_is_multiple = computed(() => {
  if (is_multiple.value)
    return true
  return props.special_multiple
})

const is_autocomplete = computed(() => {
  return filter_collection.value.select_component === 'autocomplete'
})

const final_subtype_field = computed(() => {
  return final_field_object.value.name
})

const subtype_key = computed(() => {
  const fields = filter_collection.value.fields
  const available_ids = ['id', 'key_name', 'name']
  return available_ids.find(id_key => fields.some(
    field => field.name === id_key))
})

const main_width = computed(() => props.width || 250)

function openDialog(is_add=true){
  const real_value = main_object.value[final_subtype_field.value]
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
}

function selectItem(item){
  const elem_id = filter_collection.value.pk
  const id_value = item[elem_id]
  main_object.value[final_subtype_field.value] = is_multiple
    ? [id_value]
    : id_value
  loading.value = false
  dialog_add.value = false
}

</script>

<template>

  <GenericSelect
    v-if="subtype_items && final_subtype_field"
    v-model="main_object"
    :level_name="final_subtype_field"
    :is_filter="is_filter"
    :main_width="main_width"
    :item_value="subtype_key"
    :items="subtype_items"
    :class="subtype_class"
    :is_multiple="subcategory_is_multiple"
    :label="filter_collection[subcategory_is_multiple ? 'plural_name' : 'name']"
    :required="required"
    :forced_clearable="forced_clearable"
    :collection_data="filter_collection"
    :is_autocomplete="is_autocomplete"
    @open-dialog="openDialog($event)"
  >

  </GenericSelect>

  <v-dialog
    v-model="dialog_add"
    max-width="1020"
  >
    <v-card>
      <v-card-title class="text-h5 d-flex">
        {{ filter_collection.plural_name }}
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
          :parent_collection="filter_collection.subtype"
          @select-item="selectItem"
          :main_action="main_action"
          :init_in_edition="init_in_edition"
        />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>