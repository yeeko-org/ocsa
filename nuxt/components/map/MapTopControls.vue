<script setup>
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'
import { useMapStore } from '~/store/map.js'

const mapStore = useMapStore()
const { searchableProjects } = storeToRefs(mapStore)
const { xs } = useDisplay()

// El buscador es solo un vehículo (decisions §3): al elegir, dispara la
// acción (vuela el mapa + abre el detalle vía targetProjectId) y se limpia.
// Nunca queda lleno ni refleja la selección hecha desde marcador o lista.
const search = ref(null)
// En xs el buscador se compacta a un ícono que expande la caja.
const searchOpen = ref(false)

function onSearchSelect(id) {
  if (id == null) return
  mapStore.targetProjectId = id
  if (xs.value) searchOpen.value = false
  nextTick(() => { search.value = null })
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
       extractivismo flota aparte, a su derecha (MainFilterMap). -->
  <v-sheet
    class="map-top-left d-flex align-center pa-1"
    rounded="lg"
    elevation="6"
  >
    <v-card
      variant="text"
      class="px-2 cursor-pointer"
      href="https://ocsa.ibero.mx"
      min-width="0"
    >
      <span
        class="text-h4 font-weight-bold text-primary"
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
      :items="searchableProjects"
      item-title="label"
      item-value="id"
      label="Buscar proyecto"
      density="compact"
      variant="outlined"
      hide-details
      menu-icon=""
      append-inner-icon="search"
      :autofocus="xs"
      min-width="240"
      max-width="300"
      class="ml-1"
      clearable
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
