<script setup>

import { useGeoNewStore } from "~/store/geo.js";
import { storeToRefs } from "pinia";

const geoStore = useGeoNewStore()
const { states } = storeToRefs(geoStore)

const props = defineProps({
  clearable: Boolean,
})

const state = defineModel('state', { type: Number, default: null })
const municipality = defineModel('municipality', { type: Number, default: null })
const locality = defineModel('locality', { type: Number, default: null })

onMounted(() => {
  getMunicipalities(state.value)
  getLocalities(municipality.value)
})

const loading_municipalities = ref(false)
const municipalities = ref([])
const municipalities_error = ref(null)

async function getMunicipalities(state_id) {
  if (!state_id) return
  loading_municipalities.value = true
  municipalities_error.value = null
  try {
    municipalities.value = await geoStore.getMunicipalities(state_id)
  } catch (e) {
    municipalities.value = []
    municipalities_error.value = "Error al cargar municipios"
  } finally {
    loading_municipalities.value = false
  }
}

watch(state, (newState) => {
  // console.log("Estado cambiado:", newState)
  municipality.value = null
  locality.value = null
  getMunicipalities(newState)
})

const loading_localities = ref(false)
const localities = ref([])
const localities_error = ref(null)

async function getLocalities(municipality_id) {
  if (!municipality_id) return
  loading_localities.value = true
  localities_error.value = null
  try {
    localities.value = await geoStore.getLocalities(municipality_id)
  } catch (e) {
    localities.value = []
    localities_error.value = "Error al cargar localidades"
  } finally {
    loading_localities.value = false
  }
}

watch(municipality, (newMunicipality) => {
  // console.log("Municipio cambiado:", newMunicipality)
  locality.value = null
  getLocalities(newMunicipality)
})

const commonProps = {
  itemValue: "id",
  itemTitle: "name",
  variant: "outlined",
  hideDetails: true,
  class: "ml-2 mt-2",
  maxWidth: "300",
  minWidth: "240",
}

</script>

<template>
  <v-autocomplete
    v-model="state"
    :items="states"
    item-title="short_name"
    item-value="id"
    label="Estado"
    variant="outlined"
    max-width="240"
    width="200"
    hide-details
    class="mt-2"
    :clearable="clearable"
  />
  <v-autocomplete
    v-model="municipality"
    :items="municipalities"
    label="Municipio"
    v-bind="commonProps"
    :loading="loading_municipalities"
    :clearable="clearable"
  >
  </v-autocomplete>
  <v-autocomplete
    v-if="municipality"
    v-model="locality"
    :items="localities"
    label="Localidad"
    v-bind="commonProps"
    :loading="loading_localities"

  ></v-autocomplete>
  <v-alert v-if="municipalities_error" type="error" class="mt-2">
    {{ municipalities_error }}
  </v-alert>
  <v-alert v-if="localities_error" type="error" class="mt-2">
    {{ localities_error }}
  </v-alert>
</template>
