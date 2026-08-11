<script setup>
import _debounce from 'lodash/debounce.js'
import { useDisplay } from 'vuetify'
import { useMapStore } from '~/store/map.js'

const mapStore = useMapStore()
const { xs } = useDisplay()

// El buscador es solo un vehículo (decisions §3): al elegir, dispara la
// acción (vuela el mapa + abre el detalle vía targetProjectId) y se limpia.
// Nunca queda lleno ni refleja la selección hecha desde marcador o lista.
const search = ref(null)
// En xs el buscador se compacta a un ícono que expande la caja.
const searchOpen = ref(false)

// Resultados de MiniSearch (búsqueda 100% en cliente). Vacío hasta teclear:
// no precargamos la lista completa de proyectos en el autocomplete.
const searchResults = ref([])
// Texto del input controlado (v-model:search): con `no-filter` el
// autocomplete no lo limpia solo al seleccionar, así que lo gobernamos para
// poder vaciarlo y que el buscador nunca quede lleno (§3).
const searchText = ref('')

const runSearch = _debounce(q => {
  searchResults.value = q ? mapStore.searchProjects(q) : []
}, 250)
function onSearchInput(val) {
  searchText.value = val
  runSearch(val)
}

function onSearchSelect(id) {
  if (id == null) return
  mapStore.targetProjectId = id
  if (xs.value) searchOpen.value = false
  nextTick(() => {
    search.value = null
    searchText.value = ''
    searchResults.value = []
    // Al seleccionar, Vuetify emite update:search con el label completo, que
    // reprograma una búsqueda fuzzy del título. Se cancela aquí (en el
    // microtask, ya disparados los emits) para que el menú no quede poblado.
    runSearch.cancel()
  })
}

// Enlaces al sitio público (antes en el menú "⋮" del app-bar global).
const public_links = [
  {
    title: 'Quiénes somos',
    href: 'https://ocsa.ibero.mx/quienes-somos',
  },
  {
    title: 'Materiales y publicaciones',
    href: 'https://ocsa.ibero.mx/materiales-y-publicaciones',
  },
  { title: 'Contacto', href: 'https://ocsa.ibero.mx/contacto' },
]
</script>

<template>
  <!-- Isla superior izquierda: marca OCSA + búsqueda global. La leyenda de
       extractivismo flota aparte, a su derecha (ExtractivismLegend). -->
  <v-sheet
    class="map-top-left d-flex align-center pa-1"
    rounded="lg"
    elevation="4"
  >
    <v-card
      variant="text"
      class="px-2 cursor-pointer"
      href="https://ocsa.ibero.mx"
      min-width="0"
    >
      <span
        class="text-headline-large font-weight-bold text-primary"
      >
        OCSA
      </span>
      <v-tooltip activator="parent" location="bottom">
        Ir al inicio del sitio del OCSA
      </v-tooltip>
    </v-card>

    <v-menu location="bottom">
      <template v-slot:activator="{ props }">
        <v-btn
          icon="more_vert"
          variant="text"
          density="comfortable"
          v-bind="props"
        ></v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="link in public_links"
          :key="link.href"
          :href="link.href"
          :title="link.title"
        ></v-list-item>
      </v-list>
    </v-menu>

    <!-- Buscador global (vehículo, §3). En xs se compacta a un ícono. -->
    <v-btn
      v-if="xs && !searchOpen"
      icon="search"
      variant="text"
      density="comfortable"
      @click="searchOpen = true"
    />
    <v-autocomplete
      v-else
      v-model="search"
      :items="searchResults"
      item-title="label"
      item-value="id"
      label="Buscar proyecto"
      density="compact"
      variant="outlined"
      hide-details
      no-filter
      :search="searchText"
      menu-icon=""
      append-inner-icon="search"
      :autofocus="xs"
      min-width="240"
      max-width="300"
      class="ml-1"
      clearable
      @update:search="onSearchInput"
      @update:model-value="onSearchSelect"
    ></v-autocomplete>
  </v-sheet>
</template>

<style scoped>
.map-top-left {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 3;
  background-color: #ffffffe6;
}
</style>
