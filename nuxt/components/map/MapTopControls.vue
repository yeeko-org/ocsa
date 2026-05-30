<script setup>
import { storeToRefs } from 'pinia'
import { useMapStore } from '~/store/map.js'

const mapStore = useMapStore()

const { targetProjectId, searchableProjects } = storeToRefs(mapStore)

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
      v-model="targetProjectId"
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
