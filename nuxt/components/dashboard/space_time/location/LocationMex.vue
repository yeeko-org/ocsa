<script setup>
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import {nextTick} from "vue";

const mainStore = useMainStore()
const { full_geo, cats } = storeToRefs(mainStore)
const { getGeo } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  state_field: {
    type: String,
    default: 'state',
  },
  municipality_field: {
    type: String,
    default: 'municipality',
  },
  locality_field: {
    type: String,
    default: 'locality',
  },
})

const init_loaded = ref(false)
const loading_geo = ref(false)
const total_geo_requests = ref(0)
const resolved_geo_requests = ref(0)


onMounted(() => {
  // console.log("full_main onMounted", props.full_main)
  if (props.full_main.locations) {
    getGeoUnities()
  }
})

function getGeoUnities(forced = false) {
  if (loading_geo.value)
    return
  total_geo_requests.value = 0
  resolved_geo_requests.value = 0
  if (!init_loaded.value || forced) {
    init_loaded.value = true
    const levels = ['state', 'municipality']
    levels.forEach(level => {
      updateGeo([level, props.full_main[level]])
    })
  }
}

function updateGeo([level, value]) {
  if (!value)
    return
  loading_geo.value = true
  total_geo_requests.value += 1
  getGeo([level, value]).then(() => {
    resolved_geo_requests.value += 1
    if (resolved_geo_requests.value === total_geo_requests.value)
      loading_geo.value = false
  })
}


function changeGeoValue(level, value) {
  updateGeo([level, value])
}

nextTick(() => {
  setTimeout(() => {
    // console.log("full_main nextTick")
    getGeoUnities()
  }, 10)
})

</script>

<template>
  <v-autocomplete
    v-model="full_main[state_field]"
    :items="cats.state || []"
    item-title="short_name"
    item-value="id"
    label="Estado"
    variant="outlined"
    max-width="240"
    width="200"
    hide-details
    class="mt-2"
    @update:model-value="changeGeoValue('state', $event)"
  />
  <v-autocomplete
    v-model="full_main[municipality_field]"
    :items="full_geo.state[full_main[state_field]] || []"
    item-title="name"
    item-value="id"
    label="Municipio"
    variant="outlined"
    class="ml-2 mt-2"
    max-width="300"
    min-width="240"
    hide-details
    @update:model-value="changeGeoValue('municipality', $event)"
  >
  </v-autocomplete>
  <v-autocomplete
    v-if="full_main[municipality_field]"
    v-model="full_main[locality_field]"
    :items="full_geo.municipality[full_main[municipality_field]] || []"
    item-title="name"
    item-value="id"
    label="Localidad"
    variant="outlined"
    class="ml-2 mt-2"
    max-width="320"
    min-width="240"
    hide-details
  >
  </v-autocomplete>
</template>
