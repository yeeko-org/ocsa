<script setup>
import {nextTick, onBeforeMount, onMounted, ref, watch, computed} from 'vue'
import {useMainStore} from '~/store/index'
import {storeToRefs} from 'pinia'
import _debounce from 'lodash/debounce'
import SelectFilters from "~/components/dashboard/common/SelectFilters.vue";
import PanelCommon from "~/components/dashboard/common/PanelCommon.vue";
import ProjectHeader from "~/components/dashboard/project/ProjectHeader.vue";
import ProjectSheet from "~/components/dashboard/project/ProjectSheet.vue";
import NoteSheet from "~/components/dashboard/note/NoteSheet.vue";
import NoteHeader from "~/components/dashboard/note/NoteHeader.vue";
import ActorHeader from "~/components/dashboard/actor/ActorHeader.vue";

const route = useRoute()
const group_name = route.params.group

const mainStore = useMainStore()
const { fetchCatalogs, fetchElements } = mainStore
const { double } = storeToRefs(mainStore)

onBeforeMount(() => {
  fetchCatalogs()
  changeFilters()
})

const results = ref([])
const loading_fetch = ref(false)
const visible_filters = ref([])
const filters_touched = ref(false)
const total_count = ref(0)
const current_filters = ref([])
const open_panels = ref([])
const show_details = ref(false)
// rewrite the last line in typescript
// const current_filters = ref<Array<{name: string, order: number, init_visible?: boolean, collection?: string, is_collection?: boolean, disabled?: boolean}>>([])

const group_actions_enabled = ref(false)

const pr_filters = {
  status_register: null,
  status_location: null,
  extractivism_type: null,
  megaproject_type: null,
  scale: null,
  state: null,
  status_project: null,
  social_impact: null,
  environment_impact: null,
  event_type: null,
  sub_event_type: null,
}
const comm_filters = ref({
  page: 1,
  q: "",
  sort_by: "send_petition",
  page_size: 40,
})
const final_filters = ref({
  page: 1,
  sort_by: "send_petition",
  q: "",
  page_size: 40,
  ...pr_filters,
})
const sel = ref({"selected_elems": []})
// const selected_elems = ref([])

const all_filters = [
  {
    name: "de Registro", order: 1, init_visible: true,
    collection: "status_validation", collection_type: "status",
    groups: ['project']
  },{
    name: "de Ubicación", order: 2, init_visible: false,
    collection: "status_location", disabled: true, collection_type: "status",
    groups: ['project']
  },{
    name: "Medio", order: 1, init_visible: true,
    key: "source", title: "Medio de comunicación",
    collection: "sources",
    groups: ['note']
  },{
    name: "Tipo de participante", order: 1, init_visible: true,
    key: "participant_type", title: "Tipo de participante",
    collection: "participant_types",
    groups: ['actor']
  },{
    name: "Pertenencia", order: 2, init_visible: true,
    key: "belongs", title: "Grupo de pertenencia",
    collection: "belongs", item_id: "key_name",
    groups: ['actor']
  },{
    name: "Tipo de Extr.", order: 5, init_visible: true,
    key: "extractivism_type", title: "Tipo de Extractivismo",
    collection: "deployment_capital_types",
    groups: ['project']
  },{
    name: "Tipo de MP", order: 6, init_visible: false,
    key: "megaproject_type", title: "Tipo de Megaproyecto",
    collection: "megaproject_types", groups: ['project']
  },{
    name: "Escala", order: 7, init_visible: false, key: "scale",
    collection: "scales", groups: ['project']
  },{
    name: "Estado", order: 10, init_visible: true, key: "state",
    groups: ['project']
  },{
    name: "de Proyecto", order: 14, init_visible: false,
    collection: "status_project", groups: ['project']
  },{
    name: "Af. social", order: 20, init_visible: true,
    key: "social_impact", title: "Afectación social",
    collection: "social", collection_type: "impact",
    groups: ['project']
  },
  {
    name: "Af. ambiental", order: 21, init_visible: true,
    key: "environment_impact", title: "Afectación ambiental",
    collection: "environmental", collection_type: "impact",
    groups: ['project']
  },{
    name: "Tipo de Evento", order: 25, init_visible: false,
    key: "event_type", collection: "event_types",
    groups: ['project']
  },
]

const groups = [
  {name: "Proyectos", key: "project", color: 'purple'},
  {name: "Notas", key: "note", color: 'deep-purple'},
  {name: "Actores", key: "actor", color: 'blue'},
]

const group = computed(() => groups.find(g => g.key === group_name))

const group_filters = computed(() =>
    all_filters.filter(f => f.groups.includes(group_name)) )

const sorts = [
  {text: 'Fecha de registro', value: 'send_petition'},
  {text: 'Nombre', value: 'name'},
  // {text: 'Status solicitud', value: 'status_petition'},
  // {text: 'Status de datos', value: 'status_data'},
]

onMounted(() => {
  changeFilters()
})

watch(
  final_filters, (val) => {
    // console.log("final_filters", val)
    if (val)
      debounceApplyFilters()
  },
  {deep: true}
)

function changeFilters() {
  console.log("changeFilters", group_filters.value)
  current_filters.value = group_filters.value.sort((a, b) => a.order - b.order)
  visible_filters.value = current_filters.value.filter(f => f.init_visible)
}

const debounceApplyFilters = _debounce(() => {
  console.log("debounceApplyFilters")
  applyFilters()
}, 600)

function applyFilters() {
  loading_fetch.value = true
  show_details.value = false
  // const function_name = group === 'project' ? fetchProjects : fetchNotes
  fetchElements([group_name, final_filters.value]).then(res => {
    loading_fetch.value = false
    filters_touched.value = false
    total_count.value = res.total
    results.value = res.results
    changeShowDetails()
  })
}

function changeShowDetails() {
  nextTick(() => {
    setTimeout(() => {
      show_details.value = true
    }, 10)
  })
}


function selectAll() {
  console.log("selectAll")
  // selected_elems.value = pet_file_ctrl.data_files.map(df => df.id)
}

function changeGroupActions(){
  group_actions_enabled.value = !group_actions_enabled.value
}

</script>

<template>
  <v-card class="px-3 mt-3" flat>
    <v-row class="mx-0">
      <v-col cols="12" _class="py-0">
        <v-chip-group
          v-model="visible_filters"
          multiple
          column
          color="blue"
        >
          <v-chip
            v-for="filter in current_filters"
            :key="filter.name"
            :label="!filter.collection && !filter.is_collection"
            :value="filter"
            :disabled="filter.disabled"
            class="mr-1 py-1"
            filter

            variant="tonal"
          >
            {{filter.name}}
          </v-chip>
        </v-chip-group>
      </v-col>
      <SelectFilters
        :final_filters="final_filters"
        :visible_filters="visible_filters"
      />
      <v-col cols="12" class="d-flex" order="last">
        <v-text-field
          v-model="final_filters.q"
          label="Buscar proyecto"
          outlined
          density="comfortable"
          clearable
          variant="outlined"
          hide-details
          _change="debounceApplyFilters"
          _blur="debounceApplyFilters"
          max-width="300"
        ></v-text-field>
        <v-select
          v-model="final_filters.sort_by"
          :items="sorts"
          item-title="text"
          item-value="value"
          label="Ordenar por"
          density="comfortable"
          variant="outlined"
          hide-details
          class="py-1 ml-3"
          style="max-width: 180px;"
        ></v-select>
        <v-spacer></v-spacer>
        <v-btn
          color="accent"
          variant="outlined"
          text="Mostrar acciones"
          class="mr-3"
          @click="changeGroupActions"
        ></v-btn>
        <v-menu location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              color="green"
              variant="elevated"
              dark
              append-icon="table_chart"
            >
              Descargar Excel
            </v-btn>
          </template>
          <v-list>
            <v-list-item
              title="Todos los registros"
            >
              <template v-slot:prepend>
                <v-icon icon="filter_list_off" color="grey"></v-icon>
              </template>
            </v-list-item>
            <v-list-item
              title="Solo filtrados"
            >
              <template v-slot:prepend>
                <v-icon icon="filter_list" color="accent"></v-icon>
              </template>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-col>
      <v-col cols="12" order="last">
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
            _click="wantMoveFiles"
            :disabled="!sel.selected_elems.length"
          >
            <v-icon class="mr-2">merge</v-icon>
            Fusionar
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
    <v-progress-linear
      v-if="loading_fetch"
      indeterminate
      height="10"
      color="primary"
    ></v-progress-linear>
  </v-card>
  <v-card>
    {{total_count}} Resultados
    | {{Math.ceil(total_count / final_filters.page_size)}} páginas
    <v-expansion-panels
      multiple
      v-model="open_panels"
    >
      <PanelCommon
        v-for="elem in results"
        :key="elem.id"
        :group="group"
        :main="elem"
        :show_details="show_details"
        :sel="sel"
      >
        <template #header="{openMain}">
          <ProjectHeader
            v-if="group.key === 'project'"
            :project="elem"
            :show_details="show_details"
            @open-project="openMain"
          />
          <NoteHeader
            v-else-if="group.key === 'note'"
            :note="elem"
            :show_details="show_details"
            @open-panel="openMain"
          />
          <ActorHeader
            v-else-if="group.key === 'actor'"
            :actor="elem"
            :show_details="show_details"
            @open-panel="openMain"
          />
        </template>
        <template #sheet="{full_main}">
          <ProjectSheet
            v-if="group.key === 'project'"
            :full_project="full_main"
            :show_details="show_details"
          />
          <NoteSheet
            v-else-if="group.key === 'note'"
            :full_note="full_main"
            :show_details="show_details"
          />
        </template>
      </PanelCommon>
    </v-expansion-panels>
    <v-card-actions>
      <v-pagination
        v-model="final_filters.page"
        :length="Math.ceil(total_count / final_filters.page_size)"
        :total-visible="11"
        rounded="circle"
      ></v-pagination>
    </v-card-actions>
  </v-card>
</template>
