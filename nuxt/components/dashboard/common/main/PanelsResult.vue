<script setup>

import PanelList from "~/components/dashboard/common/main/PanelList.vue";
import SummaryList from "~/components/dashboard/common/main/SummaryList.vue";
import MassiveActions from "~/components/dashboard/common/utils/MassiveActions.vue";
import DialogEdit from "~/components/dashboard/common/dialog/DialogEdit.vue";
import {useMainStore} from "~/store/index.js";

const mainStore = useMainStore()
const { mergeSimple } = mainStore

const props = defineProps({
  results: Array,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  final_filters: Object,
  total_count: Number,
  is_mini: Boolean,
  is_simple: Boolean,
  in_sheet: Boolean,
  hide_actions: Boolean,
  main_action: String,
})

const group_actions_enabled = ref(true)
const error_messages = ref([])
const sel = ref({"selected_elems": [], "show_order": false})
const edit_type = ref({
  key: 'edit', title: 'Agregar registro', btn: 'Guardar'})

const dialogEditRef = ref(null)
const dialog_edit = ref(false)
const element_to_edit = ref(null)
const selected_results = ref([])
const page_number = ref(1)
const showing = ref(15)

defineExpose({ addItem, resetPage })
const emits = defineEmits(['select-item', 'update-page-number'])

const init_indirect = computed(() => {
  return !props.results.length && props.total_count
})

const final_main_action = computed(() => {
  return sel.value.show_order ? 'order' : props.main_action
})

const results_showed = computed(() => {
  if (props.in_sheet)
    return props.results.slice(0, showing.value)
  return props.results
})

function selectAll() {
  if (sel.value.selected_elems.length === props.results.length)
    sel.value.selected_elems = []
  else
    sel.value.selected_elems = props.results.map(
        res => res[props.collection_data.pk])
  // selected_elems.value = pet_file_ctrl.data_files.map(df => df.id)
}

function wantMassiveEdit() {
  edit_type.value = {
    key: 'massive_edit', title: 'Edición masiva', btn: 'Guardar cambios'}
  selected_results.value = props.results.filter(
      res => sel.value.selected_elems.includes(res[props.collection_data.pk]))
  // element_to_edit.value = {...{}, ...selected_results.value[0]}
  element_to_edit.value = {}
  dialog_edit.value = true
}

function wantMerge() {
  // console.log("wantMerge", sel.value.selected_elems)
  edit_type.value = {
    key: 'merge', title: 'Fusión de elementos', btn: 'Fusionar'}
  selected_results.value = sel.value.selected_elems.map(
    el_id => props.results.find(res => res[props.collection_data.pk] === el_id))
  element_to_edit.value = {...{}, ...selected_results.value[0]}
  dialog_edit.value = true
}

function addItem() {
  edit_type.value = {key: 'edit', title: 'Agregar Registro', btn: 'Guardar'}
  // console.log("final_filters", props.final_filters)
  const final_filters = props.final_filters || {}
  element_to_edit.value = {...final_filters, is_new: true}
  props.collection_data.fields.forEach(field => {
    if (field.default !== undefined && field.default !== null)
      element_to_edit.value[field.name] = field.default
    else if (field.related_model === 'StatusControl'){
      if (field.name === 'status_validation')
        element_to_edit.value[field.name] = 'proposed'
      else if (field.name === 'status_register')
        element_to_edit.value[field.name] = 'draft'
    }
  })
  dialog_edit.value = true
}

function resetPage() {
  page_number.value = 1
}

function closeDialog() {
  dialog_edit.value = false
  element_to_edit.value = null
}

function saveNewElement({res, is_new}) {
  if (is_new)
    props.results.unshift(res)
  else{
    const elem_id = props.collection_data.pk
    const idx = props.results.findIndex(r => r[elem_id] === res[elem_id])
    props.results.splice(idx, 1, res)
  }
  closeDialog()
}

function mergeItems(res_main) {
  saveNewElement({res: res_main, is_new: false})
  const model_name = `${props.collection_data.app_label}.${
                        props.collection_data.model_name}`
  const elem_id = props.collection_data.pk
  const main_id = selected_results.value[0][elem_id]
  const merge_ids = selected_results.value.slice(1).map(res => res[elem_id])
  error_messages.value = []
  merge_ids.forEach(merge_id => {
    let params = {
      model_name,
      main_id,
      merge_id,
      delete_merge: true,
      // just_report: true,
    }
    const is_category = props.collection_data.is_category
    const snake_name = is_category ? props.collection_data.snake_name : null
    mergeSimple([params, snake_name]).then(res => {
      if (res.error_data) {
        console.error("Error merging items:", res.error_data)
        error_messages.value.push(
          `Error al fusionar ${merge_id}: ${res.error_data.errors}`)
        return
      }
      const idx = props.results.findIndex(
          result => result[elem_id] === merge_id)
      props.results.splice(idx, 1)
    })
  })
  dialogEditRef.value?.finishSave()
  closeDialog()
  sel.value.selected_elems = []
}

function massiveFinish(){
  sel.value.selected_elems = []
  closeDialog()
  emits('update-page-number', 1)
}

function selectItem(item) {
  emits('select-item', item)
}

</script>

<template>
  <div class="d-flex align-center">
    <span v-if="in_sheet" class="text-title-large text-black mr-6">
      <slot name="title">
      </slot>
    </span>
    <v-card
      v-if="group_actions_enabled && !is_mini && !hide_actions"
      class="px-2 py-1 d-flex align-center justify-space-between flex-grow-1"
      variant="tonal"
      color="secondary"
    >
      <v-btn
        v-if="collection_data.level !== 'secondary' && !in_sheet"
        color="accent"
        @click="addItem"
        class="mr-3"
        prepend-icon="add"
      >
        Crear
        {{collection_data.name.length > 15
          ? 'registro' : collection_data.name}}
      </v-btn>
      <v-spacer></v-spacer>
      <template
        v-if="collection_data.has.order && collection_data.level !== 'category_group'"
      >
        <v-divider vertical class="mx-2" color="blue"></v-divider>
        <v-switch
          v-model="sel.show_order"
          label="Reordenar"
          class="mr-3"
          hide-details
        ></v-switch>
      </template>
      <v-divider
        vertical
        class="mx-2"
        color="blue"
      ></v-divider>
      <MassiveActions
        v-if="results.length && collection_data.available_actions.length"
        :sel="sel"
        :results="results"
        :collection_data="collection_data"
        @select-all="selectAll"
        @want-massive-edit="wantMassiveEdit()"
        @want-merge="wantMerge()"
      />
      <v-alert
        v-else-if="init_indirect"
        type="info"
        variant="outlined"
        density="compact"
      >
        Busca manualmente | Utiliza el ícono <v-icon>search</v-icon>
      </v-alert>
      <v-alert
        v-else-if="!results.length && in_sheet"
        type="warning"
        variant="outlined"
        density="compact"
      >
        No existen {{ props.collection_data.plural_name }}
      </v-alert>
    </v-card>
  </div>
  <v-card class="mt-2" v-if="results.length">
    <span v-if="!in_sheet" class="text-grey-darken-1 text-body-small">
      Página {{page_number}} de {{Math.ceil(total_count / final_filters.page_size)}}
      | {{total_count}} Resultados
    </span>
    <v-alert
      v-if="error_messages.length"
      type="error"
      variant="outlined"
      class="mt-2"
    >
      <div v-for="(msg, idx) in error_messages" :key="idx">
        {{msg}}
      </div>
    </v-alert>
    <SummaryList
      v-if="is_mini"
      :results="results"
      :collection_data="collection_data"
      :show_details="show_details"
      @select-item="selectItem"
    />
    <template v-else>
      <PanelList
        :results="results_showed"
        :collection_data="collection_data"
        :show_details="show_details"
        :sel="sel"
        :is_simple="is_simple"
        :main_action="final_main_action"
        @select-item="selectItem"
      />
      <v-card-actions
        v-if="in_sheet && showing < results.length"
      >
        <v-spacer></v-spacer>
        <v-btn
          color="accent"
          variant="outlined"
          @click="showing += 40"
          append-icon="expand_more"
        >
          Mostrar más resultados
        </v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </template>
    <v-card-actions v-if="!in_sheet">
      <v-pagination
        v-model="page_number"
        :length="Math.ceil(total_count / final_filters.page_size)"
        :total-visible="11"
        rounded="circle"
        @update:model-value="emits('update-page-number', $event)"
      ></v-pagination>
    </v-card-actions>
  </v-card>
  <v-card
    v-else-if="!in_sheet && !init_indirect"
    class="mt-2"
  >
    <v-empty-state
      icon="manage_search"
      text="Intenta ajustar tus términos de búsqueda o filtros. A veces, términos menos específicos o consultas más amplias pueden ayudarte a encontrar lo que buscas."
      title="No encontramos coincidencias."
    ></v-empty-state>
  </v-card>
  <DialogEdit
    ref="dialogEditRef"
    v-model="element_to_edit"
    v-model:open="dialog_edit"
    :collection_data="collection_data"
    :edit_type="edit_type"
    :selected_results="selected_results"
    :ids_to_edit="sel.selected_elems"
    @close-dialog="closeDialog"
    @item-saved="saveNewElement"
    @merge-items="mergeItems"
    @massive-finish="massiveFinish"
  />
</template>

<style scoped>

</style>