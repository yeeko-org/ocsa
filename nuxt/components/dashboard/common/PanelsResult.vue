<script setup>

import PanelList from "~/components/dashboard/common/PanelList.vue";
import {ref, computed, shallowRef, nextTick} from 'vue'
import SummaryList from "~/components/dashboard/common/SummaryList.vue";
import EditCommon from "~/components/dashboard/common/EditCommon.vue";
import MassiveActions from "~/components/dashboard/utils/MassiveActions.vue";

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
  in_sheet: Boolean,
})

const group_actions_enabled = ref(true)
const sel = ref({"selected_elems": []})
const edit_type = ref({key: 'add', title: 'Agregar registro'})

const dialog_edit = ref(false)
const element_to_edit = ref(null)
const selected_results = ref([])
const page_number = ref(1)

const edit_component = shallowRef('')
defineExpose({ addItem, resetPage })
const emits = defineEmits(['select-item', 'update-page-number'])

const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const edit_name = computed(() => `${props.collection_data.model_name}Edit`)

const init_indirect = computed(() => {
  return !props.results.length && props.total_count
})

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${edit_name.value}.vue`)
  .then(module => {
    edit_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/EditGeneric.vue`).then(module => {
      edit_component.value = module.default
    })
    // edit_component.value = null
  })

function selectAll() {
  if (sel.value.selected_elems.length === props.results.length)
    sel.value.selected_elems = []
  else
    sel.value.selected_elems = props.results.map(res => res.id)
  // selected_elems.value = pet_file_ctrl.data_files.map(df => df.id)
}

function wantMassiveEdit() {
  console.log("wantMassiveEdit", sel.value.selected_elems)
  edit_type.value = {key: 'massive_edit', title: 'Edición masiva'}
  selected_results.value = props.results.filter(
      res => sel.value.selected_elems.includes(res.id))
  element_to_edit.value = {...{}, ...selected_results.value[0]}
  dialog_edit.value = true
}

function wantMerge() {
  // console.log("wantMerge", sel.value.selected_elems)
  edit_type.value = {key: 'merge', title: 'Fusión de elementos'}
  selected_results.value = sel.value.selected_elems.map(
    id => props.results.find(res => res.id === id))
  element_to_edit.value = {...{}, ...selected_results.value[0]}
  dialog_edit.value = true
}

function addItem() {
  // console.log("addItem")
  edit_type.value = {key: 'add', title: 'Agregar Registro'}
  element_to_edit.value = {}
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
    const idx = props.results.findIndex(r => r.id === res.id)
    props.results.splice(idx, 1, res)
  }
  closeDialog()
}

function selectItem(item) {
  emits('select-item', item)
}

</script>

<template>
  <v-card
    v-if="group_actions_enabled && !is_mini"
    class="px-2 py-1 d-flex align-center justify-space-between"
    variant="tonal"
    color="secondary"
  >
    <v-btn
      v-if="collection_data.level !== 'secondary'"
      color="accent"
      @click="addItem"
      class="mr-3"
      prepend-icon="add"
    >
      Agregar
      {{collection_data.name.length > 15
        ? 'registro' : collection_data.name}}
    </v-btn>
    <v-spacer></v-spacer>
    <v-divider vertical class="mx-2" color="blue"></v-divider>
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
  <v-card class="mt-2" v-if="results.length">
    <span v-if="!in_sheet" class="text-grey-darken-1 text-caption">
      Página {{final_filters.page}} de {{Math.ceil(total_count / final_filters.page_size)}}
      | {{total_count}} Resultados
    </span>
    <PanelList
      v-if="!is_mini"
      :results="results"
      :collection_data="collection_data"
      :show_details="show_details"
      :sel="sel"
    />
    <SummaryList
      v-else
      :results="results"
      :collection_data="collection_data"
      :show_details="show_details"
      @select-item="selectItem"
    />
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
  <v-dialog
    v-model="dialog_edit"
    max-width="1100"
  >
    <v-card v-if="element_to_edit">
      <v-card-title>
        {{edit_type.title}}
      </v-card-title>
      <EditCommon
        :full_main="element_to_edit"
        :collection_data="collection_data"
        @item-saved="saveNewElement"
      >
        <template v-slot:edit="{ full_main }">
          <component
            :is="edit_component"
            :full_main="element_to_edit"
            :is_massive_edit="false"
          ></component>
        </template>
      </EditCommon>

<!--      <component-->
<!--        :is="edit_component"-->
<!--        :full_main="element_to_edit"-->
<!--        :collection_data="collection_data"-->
<!--        :is_massive_edit="true"-->
<!--        _select-item="selectItem($event)"-->
<!--        @item-saved="saveNewElement"-->
<!--      ></component>-->
      <v-card-text v-if="edit_type.key !== 'add'">
        <v-divider></v-divider>
        <PanelList
          :results="selected_results"
          :collection_data="collection_data"
          :show_details="show_details"
          :sel="sel"
        />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>

</style>