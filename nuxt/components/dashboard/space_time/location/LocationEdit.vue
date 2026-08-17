<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import LocationType from "~/components/dashboard/custom_filters/LocationType.vue";
import LocationMapDialog from "~/components/dashboard/space_time/LocationMapDialog.vue";
import {LOCATION_TYPES} from "~/composables/location_types.js";
import LocationMex from "~/components/dashboard/space_time/location/LocationMex.vue";

const mainStore = useMainStore()
const { full_geo } = storeToRefs(mainStore)
const { importLocationGeo } = mainStore

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
const expanded_map = ref(false)
const geo_input = ref(null)
const importing = ref(false)
const import_error = ref('')
const import_warnings = ref([])
// El editor del mapa carga la geometría al montarse: forzar el remonte es
// la única forma de que una importación se vea sin cerrar y reabrir.
const map_key = ref(0)
const import_tooltip = 'Importar archivo (GeoJSON, .zip de shapefile o KML)'

// El mapa expandido ocupa las 12 columnas y esconde el formulario
const hide_form = computed(
    () => show_map.value && expanded_map.value && !props.second_level)

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
  // locationData es null cuando se borran todas las figuras dibujadas
  if (full_main.value.type_location === 'point') {
    const coords = locationData?.geometry?.coordinates
    full_main.value.longitude = coords ? coords[0] : null
    full_main.value.latitude = coords ? coords[1] : null
  }
  else{
    full_main.value.geojson = locationData
  }
}

async function importGeoFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  import_error.value = ''
  import_warnings.value = []
  importing.value = true
  const form_data = new FormData()
  form_data.append('file', file, file.name)
  form_data.append('type_location', full_main.value.type_location)
  const result = await importLocationGeo(form_data)
  importing.value = false
  // Sin esto, volver a elegir el mismo archivo no dispara el evento
  event.target.value = ''
  if (result?.error) {
    import_error.value = result.error
    return
  }
  import_warnings.value = result.warnings || []
  handleLocationUpdate(importedFeature(result))
  map_key.value += 1
}

// El API devuelve el punto como par de coordenadas y sin geojson, pero el
// camino de actualización del formulario espera siempre una Feature.
function importedFeature(result) {
  if (result.geojson) return result.geojson
  if (result.latitude === null || result.latitude === undefined) return null
  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'Point',
      coordinates: [result.longitude, result.latitude],
    },
  }
}

</script>

<template>
  <v-col
    v-if="!hide_form"
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
      <v-btn
        color="accent"
        class="ml-2"
        :disabled="!full_main.type_location"
        :loading="importing"
        icon
        variant="outlined"
        @click="geo_input.click()"
        v-tooltip:bottom="import_tooltip"
      >
        <v-icon>
          upload_file
        </v-icon>
      </v-btn>
      <input
        ref="geo_input"
        type="file"
        accept=".geojson,.json,.zip,.kml"
        class="d-none"
        @change="importGeoFile"
      />
    </div>
    <v-alert
      v-if="import_error"
      type="error"
      variant="tonal"
      class="mb-2"
      density="compact"
      closable
      @click:close="import_error = ''"
    >
      {{ import_error }}
    </v-alert>
    <v-alert
      v-for="msg in import_warnings"
      :key="msg"
      type="info"
      variant="tonal"
      class="mb-2"
      density="compact"
    >
      {{ msg }}
    </v-alert>
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
    :cols="second_level || expanded_map ? 12 : 6"
    :order="col_order"
  >
    <LocationMapDialog
      :key="map_key"
      :location_type="full_main.type_location"
      :full_main="full_main"
      v-model:expanded="expanded_map"
      :can_expand="!second_level"
      @update:location="handleLocationUpdate"
      @close-dialog="show_map = false"
      :close_position="close_position"
    />
  </v-col>
</template>