<script setup>

import LocationType from "~/components/dashboard/custom_filters/LocationType.vue";
import LocationMapCard from
    "~/components/dashboard/space_time/location/LocationMapCard.vue";
import {LOCATION_TYPES} from "~/composables/location_types.js";
import LocationMex from "~/components/dashboard/space_time/location/LocationMex.vue";
import {useLocationGeometry} from "~/composables/useLocationGeometry.js";
import {useClosePosition} from "~/composables/useClosePosition.js";
import LocationAlerts from
    "~/components/dashboard/space_time/location/LocationAlerts.vue";
import LocationTypeDialog from
    "~/components/dashboard/space_time/location/LocationTypeDialog.vue";
import LocationMunicipalities from
    "~/components/dashboard/space_time/location/LocationMunicipalities.vue";
import {useGeolocate} from "~/composables/useGeolocate.js";

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
// El editor del mapa carga la geometría al montarse: forzar el remonte es
// la única forma de que una importación se vea sin cerrar y reabrir.
const map_key = ref(0)
const import_error = ref('')
const import_warnings = ref([])
const overwrote_saved = ref(false)
const confirm_type_change = ref(false)
const discard_label = ref('')

const {hasGeometry, clearOtherGeometry, applyFeature, geometryLabel} =
    useLocationGeometry(full_main)

const pending_type = ref(null)

// LocationType escribe el tipo directamente en el objeto que recibe, y se
// comparte con los filtros, donde nada hay que confirmar. En vez de tocarlo,
// aquí recibe un envoltorio idéntico al modelo salvo por type_location, cuya
// escritura pasa por la confirmación: así el select no se mueve hasta que
// el usuario acepta perder la geometría anterior.
const gated_main = computed(() => new Proxy(full_main.value, {
  set(target, key, value) {
    if (key !== 'type_location') return Reflect.set(target, key, value)
    requestTypeChange(value)
    return true
  }
}))

function requestTypeChange(next_type) {
  if (!hasGeometry(full_main.value.type_location)) {
    applyTypeChange(next_type)
    return
  }
  discard_label.value = geometryLabel(full_main.value.type_location)
  pending_type.value = next_type
  confirm_type_change.value = true
}

// El mapa arma sus controles de dibujo al montarse y conserva las figuras
// ya dibujadas: sin remonte seguiría mostrando la geometría descartada.
function applyTypeChange(next_type) {
  full_main.value.type_location = next_type
  clearOtherGeometry(next_type)
  map_key.value += 1
}

function confirmTypeChange() {
  confirm_type_change.value = false
  applyTypeChange(pending_type.value)
}

const location_type_full = computed(() => LOCATION_TYPES.find(
    loc => loc.id === full_main.value.type_location))

const close_position = useClosePosition(full_main)

const {
  notices: geo_notices,
  warnings: geo_warnings,
  candidates: geo_candidates,
  candidates_text: geo_candidates_text,
  can_replace: geo_can_replace,
  has_replacement: geo_has_replacement,
  suggest: suggestGeo,
  suggestGeometry: suggestGeoGeometry,
  replaceAll: replaceGeo,
  undoReplace: undoReplaceGeo,
  clear: clearGeo,
} = useGeolocate(full_main)

function applyFeatureAndSuggest(feature) {
  applyFeature(feature)
  if (full_main.value.type_location === 'point') {
    // Sin coordenadas la llamada no sale, pero hay que avisarle igual: es
    // lo que retira las candidatas y la resolución del pin borrado.
    suggestGeo(full_main.value.latitude, full_main.value.longitude)
    return
  }
  suggestGeoGeometry(feature)
}

// Los avisos son de la importación anterior: no sobreviven a un intento
// nuevo, haya fallado o no.
function setImportError(message) {
  import_error.value = message
  import_warnings.value = []
}

// Guardar o cambiar de registro sustituye el objeto del modelo: lo que
// avisaba la importación anterior ya no tiene nada que ver con este.
watch(full_main, () => {
  import_error.value = ''
  import_warnings.value = []
  overwrote_saved.value = false
  clearGeo()
})

// El tipo que trae el archivo manda sobre el elegido en el formulario, y
// debe aplicarse antes de la geometría: applyFeature decide por él entre
// latitud/longitud y geojson.
function applyImported({feature, type_location, warnings}) {
  import_error.value = ''
  import_warnings.value = warnings
  // La medición tiene que hacerse antes de que la importación pise nada
  overwrote_saved.value = !!full_main.value.id
      && hasGeometry(full_main.value.type_location)
  if (type_location && type_location !== full_main.value.type_location) {
    // El archivo manda: el cambio de tipo no se confirma con el usuario
    full_main.value.type_location = type_location
    clearOtherGeometry(type_location)
  }
  applyFeatureAndSuggest(feature)
  map_key.value += 1
}

</script>

<template>
  <v-col
    :cols="show_map && !second_level && !expanded_map ? 6 : 12"
    :order="col_order"
  >
    <div class="d-flex align-center flex-wrap ga-1 pb-3">
      <LocationMex
        v-model:state="full_main.state"
        v-model:municipality="full_main.municipality"
        v-model:locality="full_main.locality"
      />
      <LocationType
        :full_main="gated_main"
      />
      <!-- Latitud y longitud nunca se separan: el flex-wrap del contenedor
           las partiría en renglones distintos. -->
      <div
        v-if="full_main.type_location === 'point'"
        class="d-flex ga-1 flex-nowrap"
      >
        <v-text-field
          v-model="full_main.latitude"
          label="Latitud"
          variant="outlined"
          hide-details
          style="max-width: 160px; min-width: 120px;"
        >
        </v-text-field>
        <v-text-field
          v-model="full_main.longitude"
          label="Longitud"
          variant="outlined"
          hide-details
          style="max-width: 160px; min-width: 120px;"
        >
        </v-text-field>
      </div>
      <v-btn
        v-if="!show_map"
        color="accent"
        class="ml-2"
        :disabled="!full_main.type_location"
        icon
        variant="outlined"
        @click="show_map = true"
        v-tooltip:bottom="`Abrir mapa`"
      >
        <v-icon>
          map
        </v-icon>
      </v-btn>
    </div>
    <LocationMunicipalities
      :municipalities_full="full_main.municipalities_full"
      :type_location="full_main.type_location"
    />
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
    <LocationAlerts
      v-model:import_error="import_error"
      v-model:overwrote_saved="overwrote_saved"
      :import_warnings="import_warnings"
      :geo_notices="geo_notices"
      :geo_warnings="geo_warnings"
      :candidates_text="geo_candidates_text"
      :location="full_main"
    />
    <LocationAlerts
      :helps="show_map ? location_type_full.helps : null"
    />
  </v-col>
  <v-col
    v-if="show_map"
    :cols="second_level || expanded_map ? 12 : 6"
    :order="col_order"
  >
    <LocationMapCard
      :key="map_key"
      :location_type="full_main.type_location"
      :full_main="full_main"
      v-model:expanded="expanded_map"
      :can_expand="!second_level"
      :candidates="geo_candidates"
      :can_replace="geo_can_replace"
      :has_replacement="geo_has_replacement"
      @replace="replaceGeo"
      @undo-replace="undoReplaceGeo"
      @update:location="applyFeatureAndSuggest"
      @imported="applyImported"
      @import-error="setImportError"
      @close="show_map = false"
      :close_position="close_position"
    />
  </v-col>
  <LocationTypeDialog
    v-model="confirm_type_change"
    :discard_label="discard_label"
    @confirm="confirmTypeChange"
  />
</template>