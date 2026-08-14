<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import LocationType from "~/components/dashboard/custom_filters/LocationType.vue";
import LocationMapDialog from "~/components/dashboard/space_time/LocationMapDialog.vue";
import {LOCATION_TYPES} from "~/composables/location_types.js";
import LocationMex from "~/components/dashboard/space_time/location/LocationMex.vue";

const mainStore = useMainStore()
const { full_geo } = storeToRefs(mainStore)

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  },
  second_level: Boolean,
})

const full_main = defineModel({type: Object, required: true})

const show_map = ref(false)

const location_type_full = computed(() => LOCATION_TYPES.find(
    loc => loc.id === full_main.value.type_location))


const close_position = computed(() => {
  // console.log("full_main", full_main.value)
  // console.log("full_geo", full_geo.value)
  let close_position = false
  if (full_geo.value.municipality && full_main.value.locality) {
    const mun = full_geo.value.municipality[full_main.value.municipality]
    if (mun)
      close_position = mun.find(
        loc => loc.id === full_main.value.locality)
  }
  if (close_position)
    return close_position
  if (full_geo.value.state && full_main.value.municipality) {
    const state = full_geo.value.state[full_main.value.state]
    if (state){
      close_position = state.find(
        mun => mun.id === full_main.value.municipality)
    }
  }
  return close_position
})

function handleLocationUpdate(locationData) {
  // console.log("handleLocationUpdate", locationData)
  // Update the location data based on map editor results
  if (full_main.value.type_location === 'point' && locationData.geometry?.coordinates) {
    full_main.value.longitude = locationData.geometry.coordinates[0]
    full_main.value.latitude = locationData.geometry.coordinates[1]
  }
  else{
    full_main.value.geojson = locationData
  }
}


</script>

<template>
  <v-col
    :cols="show_map && !second_level ? 6 : 12"
    :order="col_order"
  >
    <div class="d-flex align-center flex-wrap ga-1 pb-3">
      <LocationMex
        v-model:state="full_main.state"
        v-model:municipality="full_main.municipality"
        v-model:locality="full_main.locality"
      />
      <LocationType
        :full_main="full_main"
      />
      <template v-if="full_main.type_location === 'point'">
        <v-text-field
          v-model="full_main.latitude"
          label="Latitud"
          variant="outlined"
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
        class="ml-2"
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
      label="Detalles adicionales (incluyendo colonia)"
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
    :order="col_order"
  >
    <LocationMapDialog
      :location_type="full_main.type_location"
      :full_main="full_main"
      @update:location="handleLocationUpdate"
      @close-dialog="show_map = false"
      :close_position="close_position"
    />
  </v-col>
</template>