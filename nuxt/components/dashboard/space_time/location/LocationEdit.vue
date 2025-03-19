<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import {computed, nextTick} from "vue";
import LocationType from "~/components/dashboard/custom_filters/LocationType.vue";
import LocationMapDialog from "~/components/dashboard/space_time/LocationMapDialog.vue";
import {location_types} from "~/composables/location_types.js";
const mainStore = useMainStore()
const { full_geo, cats } = storeToRefs(mainStore)
const { getGeo } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
  second_level: Boolean,
})

const init_loaded = ref(false)
const loading_geo = ref(false)
const total_geo_requests = ref(0)
const resolved_geo_requests = ref(0)

const show_map = ref(false) // Control the map dialog

const location_type_full = computed(() => location_types.find(
    loc => loc.id === props.full_main.type_location))


const close_position = computed(() => {
  console.log("full_main", props.full_main)
  console.log("full_geo", full_geo.value)
  let close_position = false
  if (full_geo.value.municipality && props.full_main.locality) {
    const mun = full_geo.value.municipality[props.full_main.municipality]
    if (mun)
      close_position = mun.find(
        loc => loc.id === props.full_main.locality)
  }
  if (close_position)
    return close_position
  if (full_geo.value.state && props.full_main.municipality) {
    const state = full_geo.value.state[props.full_main.state]
    if (state){
      close_position = state.find(
        mun => mun.id === props.full_main.municipality)
    }
  }
  return close_position
})


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


function handleLocationUpdate(locationData) {
  // console.log("handleLocationUpdate", locationData)
  // Update the location data based on map editor results
  if (props.full_main.type_location === 'point' && locationData.geometry?.coordinates) {
    props.full_main.longitude = locationData.geometry.coordinates[0]
    props.full_main.latitude = locationData.geometry.coordinates[1]
  }
  else{
    props.full_main.geojson = locationData
  }
}

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
  <v-row>
    <v-col :cols="show_map && !second_level ? 6 : 12">
      <div class="d-flex align-center flex-wrap">
        <v-autocomplete
          v-model="full_main.state"
          :items="cats.state || []"
          item-title="short_name"
          item-value="id"
          label="Estado"
          variant="outlined"
          width="200"
          @update:model-value="changeGeoValue('state', $event)"
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
          min-width="240"
        >
        </v-autocomplete>
        <LocationType
          :full_main="full_main"
        />
        <template v-if="full_main.type_location === 'point'">
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
        </template>
        <v-btn
          color="accent"
          class="ml-2 mb-3"
          :disabled="!full_main.type_location"
          icon
          :variant="show_map ? 'elevated' : 'outlined'"
          @click="show_map = !show_map"
          v-tooltip:bottom="show_map ? 'Cerrar mapa' : 'Abrir mapa'"
        >
          <v-icon>
            map
          </v-icon>
        </v-btn>
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
      <v-alert
        v-if="show_map"
        type="info"
        variant="tonal"
        class="mt-3"
        density="compact"
      >
        <div
          v-for="msg in location_type_full.helps"
          :key="msg"
        >
          {{msg}}
        </div>
      </v-alert>
    </v-col>
    <v-col
      v-if="show_map"
      :cols="second_level ? 12 : 6"
    >
      <LocationMapDialog
        :location_type="full_main.type_location"
        :full_main="full_main"
        @update:location="handleLocationUpdate"
        @close-dialog="show_map = false"
        :close_position="close_position"
      />
    </v-col>
  </v-row>
</template>

<style scoped>

</style>