<script setup>
import { storeToRefs } from 'pinia'
import { useMainStore } from '~/store/index.js'
import { useMapStore } from '~/store/map.js'

const mainStore = useMainStore()
const mapStore = useMapStore()

const { exportData } = mainStore
const { target_project_id } = storeToRefs(mainStore)
const { searchableProjects } = storeToRefs(mapStore)

const loading_export = ref(false)

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

// TEMP (Sesión 1): el botón de descarga se consolidará en el panel de
// proyectos en la Sesión 2. Mantiene la función disponible mientras tanto.
function downloadProjects() {
  loading_export.value = true
  exportData(['project', {}]).then(() => {
    loading_export.value = false
  })
}
</script>

<template>
  <!-- Isla superior izquierda: marca OCSA + búsqueda global -->
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
      <span class="text-h5 font-weight-bold text-primary">OCSA</span>
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

    <v-autocomplete
      v-model="target_project_id"
      :items="searchableProjects"
      item-title="label"
      item-value="id"
      label="Buscar proyecto"
      density="compact"
      variant="outlined"
      hide-details
      menu-icon=""
      append-inner-icon="search"
      min-width="240"
      max-width="300"
      class="ml-1"
      clearable
    ></v-autocomplete>
  </v-sheet>

  <!-- TEMP (Sesión 1): descarga flotante; pasa al panel en la Sesión 2 -->
  <v-btn
    class="map-export-temp"
    color="accent"
    append-icon="download"
    variant="elevated"
    size="small"
    :loading="loading_export"
    @click="downloadProjects"
  >
    Descargar proyectos
  </v-btn>
</template>

<style scoped>
.map-top-left {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 3;
  background-color: #ffffffe6;
}

.map-export-temp {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 3;
}
</style>
