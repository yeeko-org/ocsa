<script setup>
// Búsqueda de actor por nombre (decisions §10). Al seleccionar, añade el actor
// como cápsula de filtro (filters.actors). El payload de actores (~836 KB) se
// carga lazy al primer foco; MiniSearch resuelve la búsqueda en cliente.
import { storeToRefs } from 'pinia'
import _debounce from 'lodash/debounce.js'
import { useMapStore } from '~/store/map.js'
import { useMainStore } from '~/store/index.js'

const mapStore = useMapStore()
const { mapActorsLoading } = storeToRefs(useMainStore())

const model = ref(null)
const results = ref([])
// Texto del input controlado: con `no-filter` el autocomplete no lo vacía solo
// al seleccionar; lo gobernamos para limpiarlo tras añadir la cápsula.
const searchText = ref('')

// Primer foco: dispara la carga lazy del payload (idempotente con el picker).
async function onFocus() {
  if (mapStore.actorsReady) return
  await mapStore.ensureActors()
}

const runSearch = _debounce(q => {
  results.value = q ? mapStore.searchActors(q) : []
}, 250)
function onInput(val) {
  searchText.value = val
  runSearch(val)
}

// Al elegir, añade el actor (dedup por id) y limpia el control: es un vehículo,
// no refleja la selección (esa vive en las cápsulas).
function onSelect(actor) {
  if (!actor?.id) return
  if (!mapStore.filters.actors.some(a => a.id === actor.id))
    mapStore.filters.actors.push({ id: actor.id, name: actor.name })
  nextTick(() => {
    model.value = null
    searchText.value = ''
    results.value = []
    // Cancela la búsqueda que Vuetify reprograma con el label al seleccionar
    // (el debounce es un timer; este nextTick corre después de los emits).
    runSearch.cancel()
  })
}
</script>

<template>
  <v-autocomplete
    v-model="model"
    :items="results"
    item-title="name"
    item-value="id"
    return-object
    label="Buscar actor por nombre"
    density="compact"
    variant="outlined"
    hide-details
    no-filter
    :search="searchText"
    :loading="mapActorsLoading"
    prepend-inner-icon="search"
    @focus="onFocus"
    @update:search="onInput"
    @update:model-value="onSelect"
  >
    <template #no-data>
      <div class="text-body-small text-medium-emphasis pa-3">
        {{ mapStore.actorsReady
          ? 'Escribe el nombre de un actor.'
          : 'Cargando actores…' }}
      </div>
    </template>
  </v-autocomplete>
</template>
