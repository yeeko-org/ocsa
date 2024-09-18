<script setup>
import {nextTick, onBeforeMount, onMounted, ref, watch} from 'vue'
import {useMainStore} from '~/store/index'
import {storeToRefs} from 'pinia'
import ProjectPanel from "~/components/dashboard/project/ProjectPanel.vue";
import _debounce from 'lodash/debounce'
import SelectFilters from "~/components/dashboard/common/SelectFilters.vue";
// import { useStore } from 'vuex'

// const store = useStore()
const mainStore = useMainStore()
const { fetchCatalogs, fetchProjects } = mainStore
const { double, projects } = storeToRefs(mainStore)

onBeforeMount(() => {
  fetchCatalogs()
  changeFilters()
})

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
const selected_elems = ref([])

const project_filters = [
  {
    name: "de Registro", order: 1, init_visible: true,
    collection: "status_validation", collection_type: "status",
  },{
    name: "de Ubicación", order: 2, init_visible: false,
    collection: "status_location", disabled: true, collection_type: "status"
  },{
    name: "Tipo de Extr.", order: 5, init_visible: true,
    key: "extractivism_type", title: "Tipo de Extractivismo",
    collection: "deployment_capital_types"
  },{
    name: "Tipo de MP", order: 6, init_visible: false,
    key: "megaproject_type", title: "Tipo de Megaproyecto",
    collection: "megaproject_types"
  },{
    name: "Escala", order: 7, init_visible: false, key: "scale",
    collection: "scales"
  },{
    name: "Estado", order: 10, init_visible: true, key: "state"
  },{
    name: "de Proyecto", order: 14, init_visible: false,
    collection: "status_project"
  },{
    name: "Af. social", order: 20, init_visible: true,
    key: "social_impact", title: "Afectación social",
    collection: "social", collection_type: "impact"
  },
  {
    name: "Af. ambiental", order: 21, init_visible: true,
    key: "environment_impact", title: "Afectación ambiental",
    collection: "environmental", collection_type: "impact"
  },{
    name: "Tipo de Evento", order: 25, init_visible: false,
    key: "event_type", collection: "event_types"
  },
]

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
    console.log("final_filters", val)
    if (val)
      debounceApplyFilters()
  },
  {deep: true}
)

function changeFilters() {
  current_filters.value = project_filters.sort((a, b) => a.order - b.order)
  visible_filters.value = current_filters.value.filter(f => f.init_visible)
}

const debounceApplyFilters = _debounce(() => {
  console.log("debounceApplyFilters")
  applyFilters()
}, 600)

function applyFilters() {
  loading_fetch.value = true
  show_details.value = false
  fetchProjects(final_filters.value).then(res => {
    loading_fetch.value = false
    filters_touched.value = false
    total_count.value = res.total
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
  <v-card class="px-3 mt-3" >
    <v-card-title>
      Interactúa por lo pronto mediante el menú
    </v-card-title>
  </v-card>
</template>