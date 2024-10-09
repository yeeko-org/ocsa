<script setup>
import {nextTick, onBeforeMount, onMounted, ref, watch, computed} from 'vue'
import {useMainStore} from '~/store/index'
import {storeToRefs} from 'pinia'
import _debounce from 'lodash/debounce'
import SelectFilters from "~/components/dashboard/common/SelectFilters.vue";
import PanelResult from "~/components/dashboard/common/PanelsResult.vue";

const route = useRoute()
const group_name = route.params.group

const mainStore = useMainStore()
const { fetchCatalogs, fetchElements } = mainStore
const { double, all_groups, cats_ready } = storeToRefs(mainStore)

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
const show_details = ref(false)
// rewrite the last line in typescript
// const current_filters = ref<Array<{name: string, order: number, init_visible?: boolean, collection?: string, is_collection?: boolean, disabled?: boolean}>>([])


const init_filters = {
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

const final_filters = ref({
  page: 1,
  ordering: null,
  q: "",
  page_size: 40,
  ...init_filters,
})

const all_filters = [
  {
    name: "Tipo de Extr.", order: 0, init_visible: true,
    key: "extractivism_type", title: "Tipo de Extractivismo",
    collection: "extractivism_types",
    groups: ['project', 'extractivism_type']
  },{
    name: "de Registro", order: 4, init_visible: true,
    collection: "status_register", collection_type: "status",
    groups: ['project']
  },{
    name: "de Ubicación", order: 6, init_visible: false,
    collection: "status_location", disabled: true, collection_type: "status",
    groups: ['project']
  },{
    name: "Medio", order: 1, init_visible: true,
    key: "source", title: "Medio de comunicación",
    collection: "sources",
    groups: ['note']
  },{
    name: "Tipo de participante", order: 2, init_visible: true,
    key: "participant_type", title: "Tipo de participante",
    collection: "participant_types",
    groups: ['actor']
  },{
    name: "Pertenencia", order: 3, init_visible: true,
    key: "belongs", title: "Grupo de pertenencia",
    collection: "belongs", item_id: "key_name",
    groups: ['actor']
  },{
    name: "Tipo de MP", order: 1, init_visible: false, is_autocomplete: true,
    key: "megaproject_type", title: "Tipo de Megaproyecto",
    collection: "megaproject_types", groups: ['project'],
  },{
    name: "Escala", order: 5, init_visible: false, key: "scale",
    collection: "scales", groups: ['project']
  },{
    name: "Estado", order: 6, init_visible: true, key: "state",
    collection: "states", groups: ['project']
  },{
    name: "st-Proyecto", order: 8, init_visible: false,
    title: "Status de proyecto",
    collection: "status_project", groups: ['project']
  },{
    name: "Af. social", order: 9, init_visible: true,
    key: "social_impact", title: "Afectación social",
    collection: "social", collection_type: "impact",
    groups: ['project']
  },
  {
    name: "Af. ambiental", order: 10, init_visible: true,
    key: "environment_impact", title: "Afectación ambiental",
    collection: "environmental", collection_type: "impact",
    groups: ['project']
  },{
    name: "Tipo de Evento", order: 11, init_visible: false,
    key: "event_type", collection: "event_types",
    groups: ['project', 'event']
  },
]

const group = computed(() => all_groups.value.find(g => g.key === group_name))

const group_filters = computed(() =>
    all_filters.filter(f => f.groups.includes(group_name)) )

const common_sorts = {
  'name': 'Nombre',
  'official_name': 'Nombre oficial',
  'status_validation__order': 'Status de Validación',
  'status_register__order': 'Status de Registro',
  'status_location__order': 'Status de Ubicación',
  'count': 'Cantidad',
  'id': 'Fecha de creación',
}

const final_sorts = computed(() => {
  if (!group.value.sorts && !group.value.same_sorts)
    return []
  let same_sorts = {}
  if (group.value.same_sorts)
    same_sorts = group.value.same_sorts.reduce((coll, sort) =>(
      {...coll, [sort]: common_sorts[sort]}
    ), {})
  console.log("same_sorts", same_sorts)
  let joined_sorts = {...same_sorts, ...(group.value.sorts || {})}
  return Object.entries(joined_sorts).map(([key, value]) => {
    console.log("key", key, "value", value)
    return {value: key, title: value}
  })
})

onMounted(() => {
  changeFilters()
  initCatalogs(false)
})

watch(
  final_filters, (val) => {
    // console.log("final_filters", val)
    if (val)
      debounceApplyFilters()
  },
  {deep: true}
)

watch(
  cats_ready, (val) => {
    initCatalogs(val)
  }
)

function initCatalogs(ready=null) {
  if (group.value.parent && (ready || cats_ready.value)) {
    applyFilters()
  }
}

function changeFilters() {
  current_filters.value = group_filters.value.sort((a, b) => a.order - b.order)
  console.log("group in changeFilters", group.value)
  if (group.value.simplified_filters)
    visible_filters.value = current_filters.value
  else
    visible_filters.value = current_filters.value.filter(f => f.init_visible)
}

const debounceApplyFilters = _debounce(() => {
  // console.log("debounceApplyFilters")
  applyFilters()
}, 600)

function applyFilters() {
  loading_fetch.value = true
  show_details.value = false
  // const function_name = group === 'project' ? fetchProjects : fetchNotes
  const real_group = group.value.parent ? `catalogs/${group_name}` : group_name
  fetchElements([real_group, final_filters.value]).then(res => {
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

</script>

<template>
  <v-card class="py-3" flat>
    <v-row class="mx-0">
      <v-col cols="12" _class="py-0" v-if="!group.simplified_filters">
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
        v-if="!group.simplified_filters"
        :final_filters="final_filters"
        :visible_filters="visible_filters"
      />
      <v-col
        cols="12"
        class="d-flex mb-3 mt-1 px-1"
        :order="group.simplified_filters ? 1 : 'last'"
      >
        <SelectFilters
          v-if="group.simplified_filters"
          :final_filters="final_filters"
          :visible_filters="visible_filters"
        />
        <v-text-field
          v-model="final_filters.q"
          :label="`Buscar ${group.singular || group.name || 'elementos'}`"
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
          v-if="final_sorts.length"
          v-model="final_filters.ordering"
          :items="final_sorts"
          item-title="title"
          item-value="value"
          label="Ordenar por"
          density="comfortable"
          variant="outlined"
          hide-details
          class="ml-3"
          style="max-width: 220px;"
        ></v-select>
        <v-spacer></v-spacer>
<!--        <v-btn-->
<!--          color="accent"-->
<!--          variant="outlined"-->
<!--          text="Mostrar acciones"-->
<!--          class="mr-3"-->
<!--          @click="changeGroupActions"-->
<!--        ></v-btn>-->
        <v-col cols="auto" order="12">
          <v-menu location="bottom" v-if="!group.parent">
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
      </v-col>
    </v-row>
    <v-progress-linear
      v-if="loading_fetch"
      indeterminate
      height="10"
      color="primary"
    ></v-progress-linear>
  </v-card>
  <PanelResult
    :results="results"
    :group="group"
    :show_details="show_details"
    :final_filters="final_filters"
    :total_count
  />
</template>
