<script setup>

import PanelList from "~/components/dashboard/common/PanelList.vue";
import {ref, computed, shallowRef, nextTick} from 'vue'

const props = defineProps({
  results: Array,
  group: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  final_filters: Object,
  total_count: Number,
  hide_pagination: Boolean,
})

const group_actions_enabled = ref(true)
const sel = ref({"selected_elems": []})

const dialog_edit = ref(false)
const element_to_edit = ref(null)
const selected_results = ref([])

const edit_component = shallowRef('')

const route_key = computed(() => props.group.meta_key || props.group.key)
const edit_name = computed(() => props.group.edit)
import(`~/components/dashboard/${route_key.value}/${edit_name.value}.vue`).then(module => {
  edit_component.value = module.default
})

function changeGroupActions(){
  group_actions_enabled.value = !group_actions_enabled.value
}
function selectAll() {
  console.log("selectAll")
  // selected_elems.value = pet_file_ctrl.data_files.map(df => df.id)
}

function wantMove() {
  console.log("wantMove", sel.value.selected_elems)
  selected_results.value = props.results.filter(
      res => sel.value.selected_elems.includes(res.id))
}

function wantMerge() {
  console.log("wantMerge", sel.value.selected_elems)
  selected_results.value = sel.value.selected_elems.map(
      id => props.results.find(res => res.id === id))
  element_to_edit.value = {...{}, ...selected_results.value[0]}
  dialog_edit.value = true

}

</script>

<template>
  <v-row>
    <v-col
      v-if="group_actions_enabled && sel.selected_elems.length"
      cols="12"
      order="last"
    >
      <v-card class="pa-3" variant="outlined" v-if="group_actions_enabled">
        Acciones grupales:
        <span
          v-if="sel.selected_elems.length"
          class=""
        >({{sel.selected_elems.length}}):</span>
        <v-btn
          variant="outlined"
          color="accent"
          class="ml-3"
          @click="selectAll"
        >
          <v-icon class="mr-2">fact_check</v-icon>
          Seleccionar todo
        </v-btn>
        <v-btn
          outlined
          color="accent"
          class="ml-3"
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
          @click="wantMove"
          :disabled="!sel.selected_elems.length"
        >
          <v-icon class="mr-2">app_registration</v-icon>
          Edición masiva
        </v-btn>
        <v-btn
          _disabled="!selected_files.files.length"
          outlined
          color="error"
          class="ml-3"
        >
          <v-icon class="mr-2">delete</v-icon>
          Eliminar
        </v-btn>
        <v-btn
          icon="close"
          class="float-right"
          size="small"
          variant="text"
          @click="changeGroupActions"
        ></v-btn>
      </v-card>
    </v-col>
  </v-row>
  <v-card class="mt-2">
    <template v-if="!hide_pagination">
      {{total_count}} Resultados
      | {{Math.ceil(total_count / final_filters.page_size)}} páginas
    </template>
    <PanelList
      :results="results"
      :group="group"
      :show_details="show_details"
      :sel="sel"
    />
    <v-card-actions v-if="!hide_pagination">
      <v-pagination
        v-model="final_filters.page"
        :length="Math.ceil(total_count / final_filters.page_size)"
        :total-visible="11"
        rounded="circle"
      ></v-pagination>
    </v-card-actions>
    <v-dialog
      v-model="dialog_edit"
      max-width="980"
    >
      <v-card>
        <v-card-title>
          Fusión de elementos
        </v-card-title>
        <v-card-text>
          <component
            :is="edit_component"
            :full_main="element_to_edit"
          ></component>
          <v-divider></v-divider>
          <PanelList
            :results="selected_results"
            :group="group"
            :show_details="show_details"
            :sel="sel"
          />
        </v-card-text>
        <v-card-actions class="mx-3">
          <v-btn
            color="error"
            @click="dialog_edit = false"
          >
            Cancelar
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            color="accent"
            variant="elevated"
          >
            Guardar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<style scoped>

</style>