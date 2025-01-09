<script setup>
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import {nextTick} from "vue";
const mainStore = useMainStore()
const { full_geo } = storeToRefs(mainStore)
const { getGeo, saveSimple } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})


const init_loaded = ref(false)
const loading_geo = ref(false)
const total_geo_requests = ref(0)
const resolved_geo_requests = ref(0)

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


onMounted(() => {
  // console.log("full_main onMounted", props.full_main)
  if (props.full_main.locations) {
    getGeoUnities()
  }
})

function changeGeoValue(level, value) {
  // console.log("changeGeoValue", level, value)
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
  <v-col cols="12">
    <div class="d-flex align-center flex-wrap">
      <SelectGroup
        :main_object="full_main"
        filter_group_name="states"
        :width="200"
      />
      <v-autocomplete
        v-model="full_main.municipality"
        :items="full_geo.state[full_main.state] || []"
        item-title="name"
        item-value="id"
        label="Municipio"
        variant="outlined"
        class="ml-2"
        max-width="300"
        min-width="260"
        @update:model-value="changeGeoValue('municipality', $event)"
      >
      </v-autocomplete>
      <v-autocomplete
        v-model="full_main.locality"
        :items="full_geo.municipality[full_main.municipality] || []"
        item-title="name"
        item-value="id"
        label="Localidad"
        variant="outlined"
        class="ml-2"
        max-width="320"
        min-width="260"
      >
      </v-autocomplete>
      <v-text-field
        v-model="full_main.latitude"
        label="Latitud"
        variant="outlined"
        class="mx-1"
        style="max-width: 180px;"
      >
      </v-text-field>
      <v-text-field
        v-model="full_main.longitude"
        label="Longitud"
        variant="outlined"
        style="max-width: 180px;"
      >
      </v-text-field>
    </div>
    <v-textarea
      v-model="full_main.details"
      label="Detalles adicionales"
      variant="outlined"
      class="mb-2"
      density="compact"
      hide-details
      rows="1"
      auto-grow
    >
    </v-textarea>
  </v-col>
</template>

<style scoped>

</style>