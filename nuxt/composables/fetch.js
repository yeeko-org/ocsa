import {computed, nextTick, ref, watch} from "vue";
import {useMainStore} from '~/store/index'
import _debounce from "lodash/debounce.js";

const init_filters = {
  status_register: null,
}

export const results = ref([])
export const loading_fetch = ref(false)
export const show_details = ref(false)
export const total_count = ref(0)

export const final_filters = ref({
  page: 1,
  ordering: null,
  q: "",
  page_size: 40,
  ...init_filters,
})
export const temp_reset = ref(false)

const debounceApplyFilters = _debounce(() => {
  applyFilters()
}, 600)


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

export function applyFilters() {
  const mainStore = useMainStore()
  const { fetchElements, current_collection_data } = mainStore
  // console.log("parent_collectionRef", parent_collectionRef)
  loading_fetch.value = true
  show_details.value = false
  // const function_name = group === 'project' ? fetchProjects : fetchNotes
  // const real_group = group.value.parent ? `catalogs/${current_collection}` : group_name
  // console.log('level', current_collection_data.level)
  let collection_name = current_collection_data.snake_name
  if (current_collection_data.is_category)
    collection_name = `catalogs/${collection_name}`

  fetchElements([collection_name, final_filters.value]).then(res => {
    loading_fetch.value = false
    total_count.value = res.total
    results.value = res.results
    changeShowDetails()
  })
}
