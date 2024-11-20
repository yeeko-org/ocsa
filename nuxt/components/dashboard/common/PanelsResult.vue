<script setup>

import PanelList from "~/components/dashboard/common/PanelList.vue";
import {ref, computed, shallowRef, nextTick} from 'vue'
import {saveElement} from "~/composables/save_elements.js";
import SummaryList from "~/components/dashboard/common/SummaryList.vue";
import EditCommon from "~/components/dashboard/common/EditCommon.vue";
import {el} from "vuetify/locale";

const props = defineProps({
  results: Array,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  name_field: {
    type: String,
    default: 'name',
  },
  final_filters: Object,
  total_count: Number,
  is_mini: Boolean,
})

const group_actions_enabled = ref(true)
const sel = ref({"selected_elems": []})
const edit_type = ref({key: 'add', title: 'Agregar registro'})

const dialog_edit = ref(false)
const element_to_edit = ref(null)
const selected_results = ref([])

const edit_component = shallowRef('')
defineExpose({ addItem })
const emits = defineEmits(['select-item'])

const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const edit_name = computed(() => `${props.collection_data.model_name}Edit`)
import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${edit_name.value}.vue`)
  .then(module => {
    edit_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/EditGeneric.vue`).then(module => {
      edit_component.value = module.default
    })
  })


function changeGroupActions(){
  group_actions_enabled.value = !group_actions_enabled.value
}
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
  console.log("wantMerge", sel.value.selected_elems)
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
  dialog_edit.value = true
}

function closeDialog() {
  dialog_edit.value = false
  element_to_edit.value = null
}

function saveNewElement({res, is_new}) {
  props.results.unshift(res)
  closeDialog()
}

function selectItem(item) {
  emits('select-item', item)
}

const all_selected = computed(() => {
  return props.results.length === sel.value.selected_elems.length
})

</script>

<template>
  <v-card
    v-if="group_actions_enabled && !is_mini"
    class="px-2 py-1 d-flex align-center justify-space-between"
    variant="tonal"
    _color="blue lighten-4"
    color="secondary"
  >
    <v-btn
      color="accent"
      @click="addItem"
      class="mr-3"
    >
      <v-icon>add</v-icon>
      Agregar
      {{props.collection_data.name.length > 15
        ? 'registro' : props.collection_data.name}}
    </v-btn>
    <v-spacer></v-spacer>
    <v-divider vertical class="mx-2" color="blue"></v-divider>
    Acciones grupales:
    <span
      v-if="sel.selected_elems.length"
      class=""
    >({{sel.selected_elems.length}}):</span>
    <v-btn
      :variant="all_selected ? 'elevated' : 'outlined'"
      color="accent"
      class="ml-3"
      :disabled="props.results.length < 2"
      @click="selectAll"
      size="small"
      :icon="all_selected ? 'check_box' : 'check_box_outline_blank'"
    ></v-btn>
    <v-btn
      outlined
      color="accent"
      class="ml-3"
      variant="elevated"
      @click="wantMerge"
      :disabled="!sel.selected_elems.length"
    >
      <v-icon class="mr-2">merge</v-icon>
      Fusionar
    </v-btn>
    <v-btn
      outlined
      color="accent"
      class="ml-3"
      @click="wantMassiveEdit"
      :disabled="!sel.selected_elems.length"
    >
      <v-icon class="mr-2">app_registration</v-icon>
      Edición masiva
    </v-btn>
    <v-btn
      :disabled="!sel.selected_elems.length"
      outlined
      color="error"
      class="ml-3"
    >
      <v-icon class="mr-2">delete</v-icon>
      Eliminar
    </v-btn>
    <v-btn
      v-if="false"
      icon="close"
      class="float-right"
      size="small"
      variant="text"
      @click="changeGroupActions"
    ></v-btn>
  </v-card>
  <v-card class="mt-2" v-if="results.length">
    <span class="text-grey-darken-1 text-caption">
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
    <v-card-actions>
      <v-pagination
        v-model="final_filters.page"
        :length="Math.ceil(total_count / final_filters.page_size)"
        :total-visible="11"
        rounded="circle"
      ></v-pagination>
    </v-card-actions>
  </v-card>
  <v-card
    v-else
    class="mt-2"
  >
    <v-alert type="info" variant="outlined">
      Sin resultados, cambia los filtros de búsqueda
    </v-alert>
  </v-card>
  <v-dialog
    v-model="dialog_edit"
    max-width="980"
  >
    <v-card v-if="element_to_edit">
      <v-card-title>
        {{edit_type.title}}
      </v-card-title>
      <EditCommon
        :full_main="element_to_edit"
        :collection_data="collection_data"
        :name_field="name_field"
        @item-saved="saveNewElement"
      >
        <template v-slot:edit="{ full_main }">
          <component
            :is="edit_component"
            :full_main="element_to_edit"
            :is_massive_edit="true"
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
    </v-card>
    <v-card-text v-if="edit_type.key !== 'add'">
      <v-divider></v-divider>
      <PanelList
        :results="selected_results"
        :collection_data="collection_data"
        :show_details="show_details"
        :sel="sel"
      />
    </v-card-text>
  </v-dialog>
</template>

<style scoped>

</style>