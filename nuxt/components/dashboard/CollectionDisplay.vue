<script setup>
import {computed, onMounted, ref, onBeforeMount, watch, nextTick} from "vue";
import {useMainStore} from '~/store/index'
import SelectFilters from "~/components/dashboard/common/SelectFilters.vue";
import PanelResult from "~/components/dashboard/common/PanelsResult.vue";
import {final_sorts, status_filters} from "~/composables/filters.js";
// import {
//   final_filters,
//   loading_fetch,
//   results,
//   show_details,
//   total_count,
//   temp_reset,
//   // collection_data,
// } from "~/composables/fetch.js";
import {storeToRefs} from "pinia";
import ExportButton from "~/components/dashboard/generic/ExportButton.vue";
import _debounce from "lodash/debounce.js";

const mainStore = useMainStore()

const {
  schemas,
  current_collection,
  current_collection_data,
} = storeToRefs(mainStore)
const {
  fetchElements,
} = mainStore

const props = defineProps({
  parent_collection: Object,
  level_name: String,
  filter_group: Object,
})

const init_filters = {
  status_register: null,
}

const results = ref([])
const loading_fetch = ref(false)
const show_details = ref(false)
const total_count = ref(0)
const final_filters = ref({
  page: 1,
  ordering: null,
  q: "",
  page_size: 40,
  ...init_filters,
})
const temp_reset = ref(false)

// const parent_collectionRef = toRef(props, 'parent_collection')

const visible_filters = ref([])
const current_filters = ref([])

onBeforeMount(() => {
  // console.log("beforeMount")
  resetFilters()
})

onMounted(() => {
  changeFilters()
})

const debounceApplyFilters = _debounce(() => {
  applyFilters()
}, 600)


const collection_data = computed(() => {
  // console.log("parent_collectionRef", parent_collectionRef.value)
  return props.parent_collection || current_collection_data.value
})

watch(
  final_filters, (val) => {
    // console.log("final_filters", val)
    if (!temp_reset.value)
      debounceApplyFilters()
    else
      temp_reset.value = false
  },
  {deep: true}
)

function changeShowDetails() {
  nextTick(() => {
    setTimeout(() => {
      show_details.value = true
    }, 10)
  })
}

const is_category = computed(() =>
  collection_data.value.level.includes('category'))

function applyFilters() {
  loading_fetch.value = true
  show_details.value = false
  let collection_name = collection_data.value.snake_name
  if (is_category.value)
    collection_name = `catalogs/${collection_name}`

  fetchElements([collection_name, final_filters.value]).then(res => {
    loading_fetch.value = false
    total_count.value = res.total
    results.value = res.results
    changeShowDetails()
  })
}

const simplified_filters = computed(() =>{
  return current_filters.value.length <= 3
})

function resetFilters() {
  if (!is_category.value)
    temp_reset.value = true
  final_filters.value = {
    page: 1,
    ordering: null,
    q: "",
    page_size: 40,
  }
  results.value = []
  total_count.value = 0
  show_details.value = false
  loading_fetch.value = false
  visible_filters.value = []
}

function changeFilters() {
  if (!collection_data.value)
    return
  const all_filters = collection_data.value.all_filters
  console.log("collection_data", collection_data.value)
  console.log("level_name", props.level_name)
  console.log("filter_group", props.filter_group)
  let collection_filters = all_filters.reduce((arr, f) => {
    const filter_data = schemas.value.filters_dict[f.filter_name]
    const new_filter = {...filter_data, ...f}
    if (filter_data.category_group){
      // console.log("filter_data", filter_data)
      // console.log("new_filter", new_filter)
      filter_data.category_groups.forEach(cg => {
        const short_name = `${new_filter.short_prev} ${cg.name}`
        const name = `${new_filter.prev} ${cg.name}`
        let current_filter = {
          name, short_name, category_group_value: cg.id}
        // console.log("result", {...new_filter, ...cg, ...current_filter})
        arr.push({...new_filter, ...cg, ...current_filter})
      })
      return arr
    }
    arr.push(new_filter)
    return arr
  }, [])
  const status_group = collection_data.value.status_group
  if (status_group)
    collection_filters.push(status_filters[status_group])

  // console.log("collection_filters", collection_filters)
  // f => f.collection === current_collection.value)
  // current_filters.value = group_filters.value.sort((a, b) => a.order - b.order)
  current_filters.value = collection_filters
  // console.log("group in changeFilters", group)
  if (collection_filters.length <= 3)
    visible_filters.value = current_filters.value
  else
    visible_filters.value = current_filters.value.filter(f => !f.hidden)
}

</script>

<template>
  <v-card class="pt-3" flat>
    <v-row class="mx-0" v-if="collection_data">
      <v-col cols="12" _class="py-0" v-if="!simplified_filters">
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
            {{filter.short_name || filter.name}}
          </v-chip>
        </v-chip-group>
      </v-col>
      <SelectFilters
        v-if="!simplified_filters"
        :final_filters="final_filters"
        :visible_filters="visible_filters"
      />
    </v-row>
    <v-row>
      <v-col
        cols="12"
        class="d-flex mb-2 mt-0"
        :order="simplified_filters ? 1 : 'last'"
      >
        <v-text-field
          v-model="final_filters.q"
          :label="`Buscar ${collection_data.name || 'elementos'}`"
          outlined
          density="comfortable"
          clearable
          variant="outlined"
          hide-details
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
        <SelectFilters
          v-if="simplified_filters"
          :final_filters="final_filters"
          :visible_filters="visible_filters"
        />
        <v-spacer></v-spacer>
<!--        <v-btn-->
<!--          color="accent"-->
<!--          variant="outlined"-->
<!--          text="Mostrar acciones"-->
<!--          class="mr-3"-->
<!--          @click="changeGroupActions"-->
<!--        ></v-btn>-->
        <v-col cols="auto" order="12">
          <ExportButton
            v-if="collection_data.level === 'primary'"
          />

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
    :collection_data="collection_data"
    :show_details="show_details"
    :final_filters="final_filters"
    :total_count="total_count"
  />
</template>
