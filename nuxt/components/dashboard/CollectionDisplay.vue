<script setup>
import {computed, onMounted, ref, onBeforeMount, watch, nextTick } from "vue";
import {useMainStore} from '~/store/index'
import FiltersList from "~/components/dashboard/common/select/FiltersList.vue";
import PanelsResult from "~/components/dashboard/common/PanelsResult.vue";
// import { status_filters } from "~/composables/filters.js";

import {storeToRefs} from "pinia";
import ExportButton from "~/components/dashboard/generic/ExportButton.vue";
import _debounce from "lodash/debounce.js";
import QuestionMark from "~/components/dashboard/generic/QuestionMark.vue";

const mainStore = useMainStore()

const {
  schemas,
  current_collection_data,
} = storeToRefs(mainStore)
const { fetchElements } = mainStore

const props = defineProps({
  parent_collection: Object,

  level_name: String,
  filter_group: Object,
  is_mini: Boolean,
  in_sheet: Boolean,
  init_total_count: Number,
  direct_sheet: Boolean,
  main_action: String,
  init_in_edition: Array,
  init_filters: {
    type: Object,
    default: () => ({}),
  },
})

const results = ref([])
const q_value = ref("")
const loading_fetch = ref(false)
const show_details = ref(false)
const total_count = ref(0)
const available_sorts = ref([
  {
    title: "Más recientes",
    value: "-id"
  },
  {
    title: "Más antiguos",
    value: "id"
  },
])
const final_filters = ref({
  ordering: null,  // '-id',
  page_size: 40,
})

const temp_reset = ref(false)
const visible_filters = ref([])
const current_filters = ref([])
// const panel_result = useTemplateRef('panel-result')
const childRef = ref(null)
const emits = defineEmits(['select-item'])
defineExpose({ setInitResults, changeInitFilters })

onBeforeMount(() => {
  resetFilters()
})

onMounted(() => {
  initFilters()
})

const collection_data = computed(() => {
  return props.parent_collection || current_collection_data.value
})
const simplified_filters = computed(() =>{
  if (props.is_mini)
    return false
  return current_filters.value.length <= 3
})

const sorted_results = computed(() => {
  if (!props.init_in_edition)
    return results.value
  const in_edition = results.value.filter(
    res => props.init_in_edition.includes(res.id))
  const not_in_edition = results.value.filter(
    res => !props.init_in_edition.includes(res.id))
  return [...in_edition, ...not_in_edition]
})

watch(
  final_filters, (val) => {
    if (!temp_reset.value)
      applyFilters()
    else
      temp_reset.value = false
  },
  {deep: true},
)

watch(
  q_value, (val) => {
    debounceApplyFilters()
  }
)
// const is_category = computed(() =>
//   collection_data.value.level.includes('category'))

const debounceApplyFilters = _debounce(() => {
  applyFilters()
}, 800)

function applyFilters(page=null) {
  if (page === null){
    page = 1
    if (childRef.value)
      childRef.value.resetPage()
  }
  loading_fetch.value = true
  show_details.value = false
  let collection_name = collection_data.value.snake_name
  if (collection_data.value.is_category)
    collection_name = `catalogs/${collection_name}`
  results.value = []
  const params = {
    ...final_filters.value,
    q: q_value.value,
    page: page,
    ...props.init_filters
  }
  fetchElements([collection_name, params]).then(res => {
    loading_fetch.value = false
    if (!res.results){
      total_count.value = res.length
      results.value = res
    }
    else{
      total_count.value = res.total
      results.value = res.results
    }
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

function resetFilters() {
  const coll_data = collection_data.value
  if (!coll_data.is_category && !coll_data.cat_params?.init_display)
    temp_reset.value = true
  if (props.direct_sheet)
    temp_reset.value = true
  final_filters.value = {
    ordering: collection_data.value.has.order ? 'order' : null,
    page_size: 40,
  }
  results.value = []
  total_count.value = 0
  show_details.value = false
  loading_fetch.value = false
  visible_filters.value = []
}

function initFilters() {
  // console.log("changeFilters", collection_data.value)
  if (!collection_data.value)
    return

  let collection_filters = collection_data.value.collection_filters
  current_filters.value = collection_filters

  if (props.is_mini)
    visible_filters.value = []
  else if (collection_filters.length <= 3)
    visible_filters.value = current_filters.value
  else
    visible_filters.value = current_filters.value.filter(f => !f.hidden)
}

function setInitResults(init_results){
  results.value = init_results
  total_count.value = init_results.length
}

function changeInitFilters(){
  if (!props.init_filters)
    return
  // final_filters.value
  Object.entries(props.init_filters).forEach(([key, value]) => {
    temp_reset.value = true
    final_filters.value[key] = value
  })
}

function addItem() {
  childRef.value.addItem()
  // console.log("addItem in CollectionDisplay")
  // console.log("panel_result", panel_result)
  // const ref_panel_result = panel_result.value
  // console.log("ref_panel_result", ref_panel_result)
  // ref_panel_result.addItem()
}
function selectItem(item) {
  emits('select-item', item)
}


</script>

<template>
  <v-card class="pt-3" flat style="width: 100%;">
    <template v-if="is_mini">
      <v-card-title class="text-h5 d-flex align-center">
        Busca y elige un {{ collection_data.name }}
        <v-spacer></v-spacer>
        <v-btn
          icon="close"
          variant="text"
          @click="emits('select-item', null)"
        >
        </v-btn>
      </v-card-title>
      <v-card-subtitle class="d-flex align-center">
        Si no encuentras el {{ collection_data.name }}, puedes crear uno nuevo.
        <v-spacer></v-spacer>
      </v-card-subtitle>
    </template>
    <v-row class="mx-0" v-if="collection_data">
      <v-col cols="12" class="px-0" v-if="!simplified_filters">
        <v-chip-group
          v-model="visible_filters"
          multiple
          column
          color="blue"
        >
          <v-chip
            v-for="filter in current_filters"
            :key="filter.key_name"
            :label="!filter.collection"
            :value="filter"
            :disabled="filter.disabled"
            class="mr-1 py-1"
            filter
            variant="tonal"
          >
            {{filter.short_name || filter.name || filter.title}}
          </v-chip>
        </v-chip-group>
      </v-col>
      <FiltersList
        v-if="!simplified_filters"
        :final_filters="final_filters"
        :visible_filters="visible_filters"
      />
    </v-row>
    <v-row>
      <v-col
        cols="12"
        class="d-flex mb-2 mt-0 flex-wrap"
        :order="simplified_filters ? 1 : 'last'"
      >
        <v-text-field
          v-model="q_value"
          :label="`Buscar ${collection_data.plural_name || 'elementos'}`"
          outlined
          density="compact"
          clearable
          base-color="blue"
          color="indigo"
          variant="underlined"
          hide-details
          max-width="300"
          min-width="200"
          append-inner-icon="search"
          @click:append-inner="applyFilters()"
        ></v-text-field>
        <v-select
          v-if="collection_data.available_sorts.length"
          v-model="final_filters.ordering"
          :items="collection_data.available_sorts"
          item-title="title"
          item-value="value"
          label="Ordenar por"
          density="compact"
          variant="underlined"
          hide-details
          class="mx-3"
          style="max-width: 220px; min-width: 130px;"
        ></v-select>
        <v-spacer></v-spacer>
        <FiltersList
          v-if="simplified_filters"
          :final_filters="final_filters"
          :visible_filters="visible_filters"
        />
<!--        <v-btn-->
<!--          color="accent"-->
<!--          variant="outlined"-->
<!--          text="Mostrar acciones"-->
<!--          class="mr-3"-->
<!--          @click="changeGroupActions"-->
<!--        ></v-btn>-->
        <v-col cols="auto" order="11" class="py-1">
          <ExportButton
            v-if="collection_data.level === 'primary' && !is_mini"
          />
          <v-btn
            v-else-if="is_mini"
            color="accent"
            @click="addItem"
            class="mr-3"
          >
            <v-icon left>add</v-icon>
            Agregar {{ collection_data.name }}
          </v-btn>
        </v-col>
        <v-col cols="auto" order="12" class="pl-0 py-0 pr-1">
          <QuestionMark
            size="small"
            :collection_data="collection_data"
          />
        </v-col>
      </v-col>
    </v-row>
    <v-progress-linear
      v-if="loading_fetch"
      indeterminate
      height="10"
      color="accent"
    ></v-progress-linear>
    <PanelsResult
      ref="childRef"
      :results="sorted_results"
      :collection_data="collection_data"
      :show_details="show_details"
      :final_filters="final_filters"
      :total_count="total_count || init_total_count"
      :is_mini="is_mini"
      :in_sheet="in_sheet"
      :main_action="main_action"
      @update-page-number="applyFilters($event)"
      @select-item="selectItem"
    />
  </v-card>
</template>
